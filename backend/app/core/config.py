"""Application configuration loaded from environment variables."""

from pathlib import Path
from urllib.parse import urlsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    DATABASE_URL: str
    SESSION_SECRET: str = Field(min_length=32)
    ENVIRONMENT: str = "development"
    PORT: int = Field(default=8000, ge=1, le=65535)
    FRONTEND_ORIGINS: str = ""
    UPLOAD_DIR: str = "uploads"
    UPLOAD_STORAGE_PERSISTENT: bool = False
    MAX_UPLOAD_MB: int = Field(default=10, gt=0)
    MAX_REQUEST_MB: int = Field(default=50, gt=0)
    SESSION_MAX_AGE_SECONDS: int = Field(default=86400, gt=0)
    LOGIN_RATE_LIMIT_WINDOW: int = Field(default=300, gt=0)
    LOGIN_RATE_LIMIT_MAX: int = Field(default=20, gt=0)

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Reject insecure or ephemeral production configuration at startup."""
        if self.ENVIRONMENT.lower() == "production":
            database_url = make_url(self.DATABASE_URL)
            if database_url.drivername.split("+", 1)[0] not in {"postgres", "postgresql"}:
                raise ValueError("Production requires PostgreSQL; SQLite is not supported.")
            sslmode = database_url.query.get("sslmode")
            ssl_modes = sslmode if isinstance(sslmode, tuple) else (sslmode,)
            if any(str(mode).lower() in {"disable", "allow", "prefer"} for mode in ssl_modes if mode):
                raise ValueError("Production PostgreSQL connections must require TLS.")
            if self.SESSION_SECRET.lower().startswith(("replace-", "change-me", "your-")):
                raise ValueError("Set SESSION_SECRET to a private random value in production.")
            if len(self.SESSION_SECRET) < 32:
                raise ValueError("Production SESSION_SECRET must be at least 32 characters.")
            if not self.frontend_origins_list:
                raise ValueError("Production FRONTEND_ORIGINS must contain trusted HTTPS origins only.")
            for origin in self.frontend_origins_list:
                parsed_origin = urlsplit(origin)
                try:
                    parsed_origin.port  # Validate malformed port syntax.
                except ValueError as exc:
                    raise ValueError("Production FRONTEND_ORIGINS must contain valid HTTPS origins only.") from exc
                if (
                    parsed_origin.scheme != "https"
                    or not parsed_origin.hostname
                    or "*" in parsed_origin.hostname
                    or parsed_origin.username is not None
                    or parsed_origin.password is not None
                    or parsed_origin.path
                    or parsed_origin.query
                    or parsed_origin.fragment
                ):
                    raise ValueError("Production FRONTEND_ORIGINS must contain origin-only HTTPS URLs.")
            if not self.UPLOAD_STORAGE_PERSISTENT:
                raise ValueError("Production requires UPLOAD_STORAGE_PERSISTENT=true and a persistent volume.")
            if not Path(self.UPLOAD_DIR).is_absolute():
                raise ValueError("Production UPLOAD_DIR must be an absolute persistent-volume path.")
        return self

    @property
    def frontend_origins_list(self) -> list[str]:
        """Return FRONTEND_ORIGINS split by comma as a list."""
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        """Return MAX_UPLOAD_MB converted to bytes."""
        return self.MAX_UPLOAD_MB * 1024 * 1024

    @property
    def sqlalchemy_database_url(self) -> str:
        """Normalize provider URLs for SQLAlchemy's async database drivers."""
        url = make_url(self.DATABASE_URL)
        if url.drivername in {"postgres", "postgresql"}:
            url = url.set(drivername="postgresql+psycopg")
            supabase_host = url.host and (
                url.host.endswith(".supabase.co")
                or url.host.endswith(".pooler.supabase.com")
            )
            if url.host and "sslmode" not in url.query and (
                self.ENVIRONMENT.lower() == "production" or supabase_host
            ):
                url = url.update_query_dict({"sslmode": "require"})
        return url.render_as_string(hide_password=False)

    model_config = {
        "env_file": Path(__file__).resolve().parents[2] / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
