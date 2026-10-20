import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone

from app.services import notice_service


@pytest.mark.asyncio
async def test_create_and_list_notice(auth_client: AsyncClient):
    # 1. Create notice as admin
    payload = {
        "title": "Admissions Open 2026",
        "excerpt": "Enrollment for Playgroup and Nursery Readiness is now open.",
        "body": "<p>Welcome to <strong>Little Star Playhouse</strong>!</p><script>alert('bad');</script>",
        "category": "Important",
        "status": "PUBLISHED",
        "is_pinned": True,
        "is_important": True,
    }
    create_resp = await auth_client.post("/api/notices", json=payload)
    assert create_resp.status_code == 201
    notice_data = create_resp.json()
    assert notice_data["title"] == payload["title"]
    # Check that script tag was sanitized away
    assert "<script>" not in notice_data["body"]
    assert "<strong>Little Star Playhouse</strong>" in notice_data["body"]

    # 2. Public listing contains it
    list_resp = await auth_client.get("/api/notices")
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert any(n["slug"] == notice_data["slug"] for n in items)

    # 3. Public detail contains it
    detail_resp = await auth_client.get(f"/api/notices/{notice_data['slug']}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["title"] == payload["title"]


@pytest.mark.asyncio
async def test_draft_privacy(auth_client: AsyncClient):
    # Create draft notice
    payload = {
        "title": "Secret Draft Notice",
        "excerpt": "This should not be publicly visible.",
        "body": "<p>Internal team notes.</p>",
        "category": "General",
        "status": "DRAFT",
    }
    create_resp = await auth_client.post("/api/notices", json=payload)
    assert create_resp.status_code == 201
    draft_slug = create_resp.json()["slug"]

    # Public listing must NOT contain it
    pub_resp = await auth_client.get("/api/notices")
    assert not any(n["slug"] == draft_slug for n in pub_resp.json()["items"])

    # Public detail should 404
    detail_resp = await auth_client.get(f"/api/notices/{draft_slug}")
    assert detail_resp.status_code == 404

    # Admin list CAN see it
    admin_list = await auth_client.get("/api/notices/admin/list/all")
    assert admin_list.status_code == 200
    assert any(n["slug"] == draft_slug for n in admin_list.json()["items"])


@pytest.mark.asyncio
async def test_scheduled_notice_becomes_public_when_public_feed_is_read(auth_client: AsyncClient, monkeypatch):
    scheduled_at = datetime.now(timezone.utc) + timedelta(hours=1)
    created = await auth_client.post("/api/notices", json={
        "title": "Scheduled Test Notice",
        "excerpt": "Will publish at its scheduled time",
        "body": "<p>Scheduled content</p>",
        "category": "General",
        "status": "SCHEDULED",
        "published_at": scheduled_at.isoformat(),
    })
    assert created.status_code == 201
    notice_id = created.json()["id"]

    before = await auth_client.get("/api/notices")
    assert not any(item["id"] == notice_id for item in before.json()["items"])

    monkeypatch.setattr(notice_service, "get_db_now", lambda _db: scheduled_at + timedelta(seconds=1))
    after = await auth_client.get("/api/notices")
    assert any(item["id"] == notice_id for item in after.json()["items"])

    expired_at = datetime.now(timezone.utc) - timedelta(days=1)
    expired = await auth_client.post("/api/notices", json={
        "title": "Expired Test Notice",
        "excerpt": "Must stay hidden",
        "body": "<p>Expired</p>",
        "category": "General",
        "status": "PUBLISHED",
        "published_at": (expired_at - timedelta(days=1)).isoformat(),
        "expires_at": expired_at.isoformat(),
    })
    assert expired.status_code == 201
    public_feed = await auth_client.get("/api/notices")
    assert not any(item["id"] == expired.json()["id"] for item in public_feed.json()["items"])
    assert (await auth_client.get(f"/api/notices/{expired.json()['slug']}")).status_code == 404


@pytest.mark.asyncio
async def test_notice_schedule_and_expiry_validation(auth_client: AsyncClient):
    missing_schedule = await auth_client.post("/api/notices", json={
        "title": "Missing Schedule",
        "excerpt": "Test",
        "body": "Test",
        "category": "General",
        "status": "SCHEDULED",
    })
    assert missing_schedule.status_code == 422

    now = datetime.now(timezone.utc)
    invalid_dates = await auth_client.post("/api/notices", json={
        "title": "Invalid Expiry",
        "excerpt": "Test",
        "body": "Test",
        "category": "General",
        "status": "PUBLISHED",
        "published_at": now.isoformat(),
        "expires_at": (now - timedelta(minutes=1)).isoformat(),
    })
    assert invalid_dates.status_code == 422

