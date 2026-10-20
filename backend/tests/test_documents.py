import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.models.stored_file import StoredFile
from app.services import document_service


@pytest.mark.asyncio
async def test_document_crud(auth_client: AsyncClient, test_session_factory):
    # Seed a stored file record
    async with test_session_factory() as db:
        file_id = uuid4()
        sf = StoredFile(
            id=file_id,
            storage_key=f"{file_id}.pdf",
            original_filename="sample-guide.pdf",
            display_filename="sample-guide.pdf",
            mime_type="application/pdf",
            extension=".pdf",
            file_size=1024,
            sha256_checksum="0" * 64,
            is_public=True,
        )
        db.add(sf)
        await db.commit()

    # 1. Create document
    create_payload = {
        "title": "Annual Parent Handbook",
        "description": "Comprehensive guide for parents.",
        "category": "Parent Guidelines",
        "file_id": str(file_id),
        "status": "PUBLISHED",
    }
    create_resp = await auth_client.post("/api/documents", json=create_payload)
    assert create_resp.status_code == 201
    doc_id = create_resp.json()["id"]

    # 2. Public listing has it
    list_resp = await auth_client.get("/api/documents")
    assert list_resp.status_code == 200
    assert any(d["id"] == doc_id for d in list_resp.json()["items"])

    # 3. Update document
    update_payload = {"title": "Updated Parent Handbook"}
    update_resp = await auth_client.put(f"/api/documents/{doc_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Parent Handbook"

    # 4. Delete document
    del_resp = await auth_client.delete(f"/api/documents/{doc_id}")
    assert del_resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduled_document_and_file_reference_validation(auth_client: AsyncClient, test_session_factory, monkeypatch):
    file_id = uuid4()
    async with test_session_factory() as db:
        db.add(StoredFile(
            id=file_id,
            storage_key=f"{file_id}.pdf",
            original_filename="scheduled.pdf",
            display_filename="scheduled.pdf",
            mime_type="application/pdf",
            extension=".pdf",
            file_size=100,
            sha256_checksum="1" * 64,
            is_public=False,
        ))
        await db.commit()

    scheduled_at = datetime.now(timezone.utc) + timedelta(hours=1)
    created = await auth_client.post("/api/documents", json={
        "title": "Scheduled resource",
        "description": "Test",
        "category": "Other Documents",
        "file_id": str(file_id),
        "status": "SCHEDULED",
        "published_at": scheduled_at.isoformat(),
    })
    assert created.status_code == 201
    document_id = created.json()["id"]
    before = await auth_client.get("/api/documents")
    assert not any(item["id"] == document_id for item in before.json()["items"])

    monkeypatch.setattr(document_service, "get_db_now", lambda _db: scheduled_at + timedelta(seconds=1))
    after = await auth_client.get("/api/documents")
    assert any(item["id"] == document_id for item in after.json()["items"])

    expired_at = datetime.now(timezone.utc) - timedelta(days=1)
    expired = await auth_client.post("/api/documents", json={
        "title": "Expired Resource",
        "description": "Must stay hidden",
        "category": "Other Documents",
        "file_id": str(file_id),
        "status": "PUBLISHED",
        "published_at": (expired_at - timedelta(days=1)).isoformat(),
        "expires_at": expired_at.isoformat(),
    })
    assert expired.status_code == 201
    public_docs = await auth_client.get("/api/documents")
    assert not any(item["id"] == expired.json()["id"] for item in public_docs.json()["items"])

    missing_file = await auth_client.post("/api/documents", json={
        "title": "Missing file",
        "description": "Test",
        "category": "Other Documents",
        "file_id": str(uuid4()),
        "status": "PUBLISHED",
    })
    assert missing_file.status_code == 422

