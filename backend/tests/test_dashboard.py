import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_metrics(auth_client: AsyncClient):
    resp = await auth_client.get("/api/admin/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "published_notices" in data
    assert "draft_notices" in data
    assert "scheduled_notices" in data
    assert "published_documents" in data
    assert "total_inquiries" in data
    assert isinstance(data["recent_notices"], list)
    assert isinstance(data["recent_uploads"], list)

