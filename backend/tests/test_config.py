import pytest
from pydantic import ValidationError

from app.core.config import Settings


def production_settings(**overrides) -> Settings:
    values = {
        "DATABASE_URL": "postgresql://playhouse:secret@db.example.test:5432/playhouse",
        "SESSION_SECRET": "test-only-session-secret-at-least-32-chars",
        "ENVIRONMENT": "production",
        "FRONTEND_ORIGINS": "https://playhouse.example.test",
        "UPLOAD_DIR": "/var/lib/playhouse/uploads",
        "UPLOAD_STORAGE_PERSISTENT": True,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_production_accepts_postgresql_and_origin_only_https_configuration():
    settings = production_settings()
    assert settings.sqlalchemy_database_url.startswith("postgresql+psycopg://")
    assert "sslmode=require" in settings.sqlalchemy_database_url
    assert settings.frontend_origins_list == ["https://playhouse.example.test"]


@pytest.mark.parametrize("database_url", [
    "sqlite+aiosqlite:///local.db",
    "mysql+pymysql://user:pass@db.example.test/playhouse",
])
def test_production_rejects_non_postgresql_databases(database_url):
    with pytest.raises(ValidationError, match="Production requires PostgreSQL"):
        production_settings(DATABASE_URL=database_url)


@pytest.mark.parametrize("origin", [
    "http://playhouse.example.test",
    "https://playhouse.example.test/admin",
    "https://user:pass@playhouse.example.test",
    "https://*.playhouse.example.test",
    "https://playhouse.example.test?redirect=elsewhere",
    "https://playhouse.example.test:invalid",
])
def test_production_rejects_non_origin_frontend_urls(origin):
    with pytest.raises(ValidationError, match="FRONTEND_ORIGINS"):
        production_settings(FRONTEND_ORIGINS=origin)


def test_production_rejects_postgresql_tls_downgrade():
    with pytest.raises(ValidationError, match="must require TLS"):
        production_settings(
            DATABASE_URL="postgresql://user:pass@db.example.test/playhouse?sslmode=disable"
        )


def test_supabase_pooler_url_gets_tls_in_development_too():
    settings = Settings(
        _env_file=None,
        DATABASE_URL="postgresql://user:pass@aws-0-region.pooler.supabase.com:5432/postgres",
        SESSION_SECRET="test-only-session-secret-at-least-32-chars",
        ENVIRONMENT="development",
    )
    assert "sslmode=require" in settings.sqlalchemy_database_url


def test_resource_and_rate_limit_values_must_be_positive():
    with pytest.raises(ValidationError):
        production_settings(MAX_REQUEST_MB=0)
    with pytest.raises(ValidationError):
        production_settings(SESSION_MAX_AGE_SECONDS=-1)
    with pytest.raises(ValidationError):
        production_settings(PORT=70000)


def test_production_supabase_storage_does_not_require_a_persistent_disk():
    configured = production_settings(
        STORAGE_BACKEND="supabase",
        SUPABASE_URL="https://project-ref.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="private-test-service-role-key",
        SUPABASE_STORAGE_BUCKET="playhouse-uploads",
        UPLOAD_STORAGE_PERSISTENT=False,
    )
    assert configured.STORAGE_BACKEND == "supabase"


def test_production_supabase_storage_requires_all_provider_settings():
    with pytest.raises(ValidationError, match="SUPABASE_URL"):
        production_settings(STORAGE_BACKEND="supabase")


def test_production_rejects_unknown_storage_backend():
    with pytest.raises(ValidationError, match="STORAGE_BACKEND"):
        production_settings(STORAGE_BACKEND="remote")
