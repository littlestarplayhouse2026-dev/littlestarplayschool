"""Authentication endpoints: login, logout, me, csrf, and change-password."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db, rate_limit_login, verify_csrf
from app.core.security import (
    generate_csrf_token,
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from app.models.login_attempt import LoginAttempt
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse)
async def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit_login),
) -> AuthResponse:
    """Authenticate administrator, create session, and set HttpOnly session cookie."""
    client_ip = request.client.host if request.client else "0.0.0.0"

    identifier = credentials.account_identifier
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is required",
        )

    # Authenticate only by the unique username; display names are not credentials.
    result = await db.execute(select(User).where(func.lower(User.username) == identifier.lower()))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(credentials.password, user.password_hash) or not user.is_active:
        # Record failed attempt
        db.add(LoginAttempt(ip_address=client_ip, success=False))
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Clear previous failed attempts for this IP on successful login
    await db.execute(delete(LoginAttempt).where(LoginAttempt.ip_address == client_ip, LoginAttempt.success.is_(False)))
    db.add(LoginAttempt(ip_address=client_ip, success=True))

    # Generate session token & CSRF token
    raw_token = generate_session_token()
    token_hash = hash_session_token(raw_token)
    csrf_token = generate_csrf_token()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.SESSION_MAX_AGE_SECONDS)

    session_obj = Session(
        user_id=user.id,
        token_hash=token_hash,
        csrf_token=csrf_token,
        ip_address=client_ip,
        user_agent=request.headers.get("User-Agent", "")[:512],
        expires_at=expires_at,
    )
    db.add(session_obj)
    await db.commit()

    # Set secure HttpOnly session cookie
    is_production = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="session_id",
        value=raw_token,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=is_production,
        samesite="none" if is_production else "lax",
        path="/",
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
        csrf_token=csrf_token,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    _csrf: None = Depends(verify_csrf),
) -> MessageResponse:
    """Revoke current session and clear session cookie."""
    token = request.cookies.get("session_id")
    if token:
        token_hash = hash_session_token(token)
        result = await db.execute(select(Session).where(Session.token_hash == token_hash))
        session_obj = result.scalar_one_or_none()
        if session_obj:
            await db.delete(session_obj)
            await db.commit()

    response.delete_cookie(key="session_id", path="/")
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=AuthResponse)
async def get_me(
    request: Request,
    user: User = Depends(get_current_user),
) -> AuthResponse:
    """Return currently authenticated user and active CSRF token."""
    session_obj = getattr(request.state, "session", None)
    csrf_token = session_obj.csrf_token if session_obj else ""
    return AuthResponse(
        user=UserResponse.model_validate(user),
        csrf_token=csrf_token,
    )


@router.get("/csrf")
async def get_csrf(request: Request, user: User = Depends(get_current_user)) -> dict[str, str]:
    """Retrieve CSRF token for the authenticated user."""
    session_obj = getattr(request.state, "session", None)
    return {"csrf_token": session_obj.csrf_token if session_obj else ""}


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: Request,
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _csrf: None = Depends(verify_csrf),
) -> MessageResponse:
    """Change password for currently authenticated user."""
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user.password_hash = hash_password(data.new_password)
    current_session = getattr(request.state, "session", None) if request else None
    sessions_result = await db.execute(select(Session).where(Session.user_id == user.id))
    for active_session in sessions_result.scalars().all():
        if current_session is None or active_session.id != current_session.id:
            await db.delete(active_session)
    await db.commit()

    return MessageResponse(message="Password successfully updated")
