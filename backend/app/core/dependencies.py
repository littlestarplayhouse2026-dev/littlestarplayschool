"""FastAPI dependency functions for authentication, authorization, and rate limiting."""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import hash_session_token
from app.db.session import get_async_session
from app.models.login_attempt import LoginAttempt
from app.models.session import Session
from app.models.user import User
from app.utils.datetime_utils import get_db_now


async def get_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncSession:  # type: ignore[misc]
    """Yield an async database session."""
    yield session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Look up the session token from the 'session_id' cookie and return the authenticated user.

    Raises HTTPException 401 if the cookie is missing, the session is invalid, or it has expired.
    """
    token = request.cookies.get("session_id")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token_hash = hash_session_token(token)
    result = await db.execute(
        select(Session)
        .options(selectinload(Session.user))
        .where(Session.token_hash == token_hash)
    )
    session_obj = result.scalar_one_or_none()

    if session_obj is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )

    exp_at = session_obj.expires_at
    if exp_at.tzinfo is None:
        exp_at = exp_at.replace(tzinfo=timezone.utc)
    if exp_at <= datetime.now(timezone.utc):
        # Clean up expired session
        await db.delete(session_obj)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    user = session_obj.user
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account deactivated",
        )

    # Attach session info to request state for CSRF checks
    request.state.session = session_obj
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Raise 403 unless the current user has the ADMIN role."""
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def require_editor_or_admin(user: User = Depends(get_current_user)) -> User:
    """Raise 403 unless the current user is an ADMIN or EDITOR."""
    if user.role not in ("ADMIN", "EDITOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor or admin access required",
        )
    return user


async def verify_csrf(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> None:
    """For non-GET requests from cookie-authenticated users, verify the X-CSRF-Token header.

    This dependency should be added to state-changing endpoints.
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    # Only enforce CSRF if there is a session cookie
    token = request.cookies.get("session_id")
    if not token:
        return

    token_hash = hash_session_token(token)
    result = await db.execute(
        select(Session).where(Session.token_hash == token_hash)
    )
    session_obj = result.scalar_one_or_none()
    if session_obj is None:
        return  # Auth dependency will handle 401

    csrf_header = request.headers.get("X-CSRF-Token", "")
    if not csrf_header or csrf_header != session_obj.csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )


async def rate_limit_login(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Check login attempt rate from the client IP. Raises 429 if rate exceeded."""
    client_ip = _get_client_ip(request)
    window_start = get_db_now(db) - timedelta(seconds=settings.LOGIN_RATE_LIMIT_WINDOW)

    result = await db.execute(
        select(func.count(LoginAttempt.id)).where(
            LoginAttempt.ip_address == client_ip,
            LoginAttempt.success.is_(False),
            LoginAttempt.attempted_at >= window_start,
        )
    )
    count = result.scalar_one()

    if count >= settings.LOGIN_RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )


def _get_client_ip(request: Request) -> str:
    """Return the ASGI peer address; caller supplied forwarding headers are untrusted."""
    return request.client.host if request.client else "0.0.0.0"
