"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    DATABASE_URL: str
    SESSION_SECRET: str = Field(min_length=32)
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    FRONTEND_ORIGINS: str = "http://localhost:3000"
    UPLOAD_DIR: str = "uploads"
    UPLOAD_STORAGE_PERSISTENT: bool = False
    MAX_UPLOAD_MB: int = 10
    MAX_REQUEST_MB: int = 50
    SESSION_MAX_AGE_SECONDS: int = 86400
    LOGIN_RATE_LIMIT_WINDOW: int = 300
    LOGIN_RATE_LIMIT_MAX: int = 20

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Reject insecure or ephemeral production configuration at startup."""
        if self.ENVIRONMENT.lower() == "production":
            if self.DATABASE_URL.lower().startswith(("sqlite:", "sqlite+")):
                raise ValueError("Production requires PostgreSQL; SQLite is not supported.")
            if self.SESSION_SECRET.lower().startswith(("replace-", "change-me", "your-")):
                raise ValueError("Set SESSION_SECRET to a private random value in production.")
            if len(self.SESSION_SECRET) < 32:
                raise ValueError("Production SESSION_SECRET must be at least 32 characters.")
            if not self.frontend_origins_list or any(
                not origin.startswith("https://") for origin in self.frontend_origins_list
            ):
                raise ValueError("Production FRONTEND_ORIGINS must contain trusted HTTPS origins only.")
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
            if url.host and url.host.endswith(".supabase.co") and "sslmode" not in url.query:
                url = url.update_query_dict({"sslmode": "require"})
        return url.render_as_string(hide_password=False)

    model_config = {
        "env_file": Path(__file__).resolve().parents[2] / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
