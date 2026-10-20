import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user: User):
    response = await client.post(
        "/api/auth/login",
        json={"username": admin_user.username, "password": "Secret123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == admin_user.username
    assert "csrf_token" in data
    assert "session_id" in response.cookies


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, admin_user: User):
    response = await client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_with_username_success(client: AsyncClient, admin_user: User):
    response = await client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "Secret123!"},
    )
    assert response.status_code == 200
    assert response.json()["user"]["username"] == admin_user.username


@pytest.mark.asyncio
async def test_get_me_authenticated(auth_client: AsyncClient, admin_user: User):
    response = await auth_client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["user"]["username"] == admin_user.username


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(auth_client: AsyncClient):
    logout_resp = await auth_client.post("/api/auth/logout")
    assert logout_resp.status_code == 200

    me_resp = await auth_client.get("/api/auth/me")
    assert me_resp.status_code == 401


@pytest.mark.asyncio
async def test_production_login_cookie_is_secure_and_cross_origin_capable(client: AsyncClient, admin_user: User, monkeypatch):
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    response = await client.post("/api/auth/login", json={"username": admin_user.username, "password": "Secret123!"})
    assert response.status_code == 200
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "secure" in cookie and "samesite=none" in cookie


@pytest.mark.asyncio
async def test_viewer_role_cannot_access_editor_or_admin_endpoints(client: AsyncClient, test_session_factory):
    async with test_session_factory() as db:
        db.add(User(
            username="viewer",
            password_hash=hash_password("ViewerPass123!"),
            display_name="Read Only Viewer",
            role="VIEWER",
            is_active=True,
        ))
        await db.commit()

    login = await client.post("/api/auth/login", json={"username": "viewer", "password": "ViewerPass123!"})
    assert login.status_code == 200
    assert (await client.get("/api/admin/dashboard")).status_code == 403
    assert (await client.get("/api/notices/admin/list/all")).status_code == 403

