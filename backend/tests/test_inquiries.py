import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthorized_inquiries(client: AsyncClient):
    # Public unauthenticated client cannot view inquiries
    forbidden_resp = await client.get("/api/inquiries/admin/list/all")
    assert forbidden_resp.status_code == 401


@pytest.mark.asyncio
async def test_submit_inquiry(client: AsyncClient, auth_client: AsyncClient):
    payload = {
        "parent_name": "Ramesh Sharma",
        "phone": "+977-9801234567",
        "email": "ramesh@example.com",
        "child_age": "3 years",
        "program": "Playgroup",
        "message": "We would like to schedule a campus tour this week.",
    }
    resp = await client.post("/api/inquiries", json=payload)
    assert resp.status_code == 201
    assert "Thank you" in resp.json()["message"]

    # Admin can view inquiries
    admin_resp = await auth_client.get("/api/inquiries/admin/list/all")
    assert admin_resp.status_code == 200
    items = admin_resp.json()["items"]
    assert any(i["parent_name"] == "Ramesh Sharma" for i in items)


@pytest.mark.asyncio
async def test_inquiry_search_status_detail_and_delete(auth_client: AsyncClient):
    submitted = await auth_client.post("/api/inquiries", json={
        "parent_name": "Synthetic Parent",
        "phone": "+977 9800000011",
        "email": "synthetic@example.com",
        "message": "Synthetic workflow record",
    })
    assert submitted.status_code == 201
    inquiry_id = submitted.json()["id"]

    searched = await auth_client.get("/api/inquiries/admin/list/all", params={"search": "Synthetic Parent"})
    assert searched.status_code == 200
    assert searched.json()["total"] == 1

    details = await auth_client.get(f"/api/inquiries/admin/{inquiry_id}")
    assert details.status_code == 200
    assert details.json()["email"] == "synthetic@example.com"

    updated = await auth_client.patch(f"/api/inquiries/admin/{inquiry_id}", json={"status": "REVIEWED"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "REVIEWED"
    filtered = await auth_client.get("/api/inquiries/admin/list/all", params={"status_filter": "REVIEWED"})
    assert any(item["id"] == inquiry_id for item in filtered.json()["items"])

    deleted = await auth_client.delete(f"/api/inquiries/admin/{inquiry_id}")
    assert deleted.status_code == 200
    assert (await auth_client.get(f"/api/inquiries/admin/{inquiry_id}")).status_code == 404


@pytest.mark.asyncio
async def test_inquiry_rate_limit_and_honeypot(client: AsyncClient, auth_client: AsyncClient):
    payload = {"parent_name": "Rate Limit Test", "phone": "+977 9800000022", "message": "Synthetic"}
    for _ in range(5):
        assert (await client.post("/api/inquiries", json=payload)).status_code == 201
    limited = await client.post("/api/inquiries", json=payload)
    assert limited.status_code == 429

    # The honeypot returns a harmless success response without adding an inquiry.
    before = (await auth_client.get("/api/inquiries/admin/list/all")).json()["total"]
    trap = await client.post("/api/inquiries", json={**payload, "website": "spam"})
    after = (await auth_client.get("/api/inquiries/admin/list/all")).json()["total"]
    assert trap.status_code == 201 and trap.json()["id"] == ""
    assert after == before

