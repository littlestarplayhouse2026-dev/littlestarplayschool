"""Pytest fixtures for Little Star Playhouse backend tests."""

import os
import shutil
import tempfile
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.notice import Notice
from app.models.user import User

# Test in-memory / temporary database
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def test_upload_dir(monkeypatch):
    """Provide isolated upload directory for tests."""
    temp_dir = tempfile.mkdtemp()
    monkeypatch.setattr(settings, "UPLOAD_DIR", temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def test_engine():
    """Create a temporary test engine and tables."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session_factory(test_engine):
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def client(test_session_factory, monkeypatch) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client with mocked DB session."""
    from app.db import session as db_session_module
    from app.core import dependencies as deps_module

    monkeypatch.setattr(db_session_module, "async_session_factory", test_session_factory)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as s:
            yield s

    from app.core.dependencies import get_db
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(test_session_factory) -> User:
    """Create a seeded admin user."""
    async with test_session_factory() as db:
        user = User(
            id=uuid4(),
            username="testadmin",
            password_hash=hash_password("Secret123!"),
            display_name="Test Admin",
            role="ADMIN",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


@pytest.fixture
async def auth_client(client: AsyncClient, admin_user: User) -> AsyncClient:
    """Client with authenticated session and CSRF header configured."""
    resp = await client.post(
        "/api/auth/login",
        json={"username": admin_user.username, "password": "Secret123!"},
    )
    assert resp.status_code == 200
    csrf_token = resp.json()["csrf_token"]
    client.headers["X-CSRF-Token"] = csrf_token
    return client

