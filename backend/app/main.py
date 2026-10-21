"""FastAPI application entry point for Little Star Playhouse backend."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.session import async_session_factory
from app.core.security import hash_password
from app.models.user import User
from sqlalchemy import func, select

logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT != "development" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("littlestar")


class RequestSizeLimitMiddleware:
    """Enforce a streaming body-size cap, including requests without Content-Length."""

    def __init__(self, app, max_bytes: int | None = None):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        max_bytes = self.max_bytes or settings.MAX_REQUEST_MB * 1024 * 1024
        content_length = next(
            (value.decode("latin-1") for name, value in scope.get("headers", []) if name.lower() == b"content-length"),
            None,
        )
        try:
            if content_length is not None and int(content_length) > max_bytes:
                await self._reject(send)
                return
        except ValueError:
            await self._reject(send)
            return

        received = 0
        too_large = False
        buffered_response = []

        async def limited_receive():
            nonlocal received, too_large
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > max_bytes:
                    too_large = True
                    return {"type": "http.request", "body": b"", "more_body": False}
            return message

        async def tracked_send(message):
            if too_large:
                buffered_response.append(message)
            else:
                await send(message)

        await self.app(scope, limited_receive, tracked_send)
        if too_large:
            await self._reject(send)

    @staticmethod
    async def _reject(send):
        body = b'{"detail":"Request body too large"}'
        headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode("ascii")),
            (b"x-content-type-options", b"nosniff"),
            (b"x-frame-options", b"DENY"),
            (b"referrer-policy", b"strict-origin-when-cross-origin"),
        ]
        if settings.ENVIRONMENT == "production":
            headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))
        await send({"type": "http.response.start", "status": 413, "headers": headers})
        await send({"type": "http.response.body", "body": body})


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifespan handler."""
    logger.info("Starting Little Star Playhouse API (env=%s)...", settings.ENVIRONMENT)

    # Local storage needs a directory; Supabase storage must never fall back to disk.
    if settings.STORAGE_BACKEND.strip().lower() == "local":
        upload_path = Path(settings.UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)
        logger.info("Local upload directory configured at: %s", upload_path.resolve())
    else:
        logger.info("Persistent file storage configured with Supabase Storage")

    # Temporary dashboard-only recovery path for deployments without shell access.
    # Remove both environment variables as soon as the service starts successfully.
    if settings.ADMIN_BOOTSTRAP_USERNAME and settings.ADMIN_BOOTSTRAP_PASSWORD:
        async with async_session_factory() as db:
            result = await db.execute(
                select(User).where(func.lower(User.username) == settings.ADMIN_BOOTSTRAP_USERNAME.lower())
            )
            admin = result.scalar_one_or_none()
            if admin is not None and admin.role != "ADMIN":
                raise RuntimeError("ADMIN_BOOTSTRAP_USERNAME belongs to a non-administrator account")
            if admin is None:
                admin = User(
                    username=settings.ADMIN_BOOTSTRAP_USERNAME,
                    display_name="Playhouse Administrator",
                    role="ADMIN",
                    is_active=True,
                    password_hash=hash_password(settings.ADMIN_BOOTSTRAP_PASSWORD),
                )
                db.add(admin)
            else:
                admin.password_hash = hash_password(settings.ADMIN_BOOTSTRAP_PASSWORD)
                admin.is_active = True
            await db.commit()
            logger.warning("Temporary administrator bootstrap applied for username '%s'; remove bootstrap variables now.", admin.username)

    # Database schema changes are applied explicitly with Alembic. Accounts and
    # content are created through the protected CLI and admin interface.

    yield

    logger.info("Shutting down Little Star Playhouse API...")
    await engine.dispose()


app = FastAPI(
    title="Little Star Playhouse API",
    description="Backend API for Little Star Playhouse preschool in Janakpurdham, Nepal.",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

@app.middleware("http")
async def security_headers_and_request_limit(request: Request, call_next):
    """Set browser security headers on normal API responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token", "Accept"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled errors and return generic 500 in production, detailed in dev."""
    logger.exception("Unhandled server exception: %s", exc)
    detail = str(exc) if settings.ENVIRONMENT == "development" else "Internal server error"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )


# Mount the combined API router under /api
app.include_router(api_router)
