import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "version": "1.0.0"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


@pytest.mark.asyncio
async def test_chunked_request_body_limit(client: AsyncClient, monkeypatch):
    monkeypatch.setattr(settings, "MAX_REQUEST_MB", 1)

    async def oversized_body():
        yield b"{" + b" " * (600 * 1024)
        yield b" " * (500 * 1024) + b"}"

    response = await client.post(
        "/api/inquiries",
        content=oversized_body(),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413, response.text

