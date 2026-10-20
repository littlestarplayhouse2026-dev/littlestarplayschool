import pytest
from pathlib import Path
from httpx import ASGITransport, AsyncClient
from uuid import uuid4
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.stored_file import StoredFile
from app.models.user import User
from app.main import app


@pytest.mark.asyncio
async def test_upload_validation_authorization_download_and_delete(auth_client: AsyncClient, test_upload_dir):
    # A valid PNG signature is sufficient for the application's current signature check.
    payload = b"\x89PNG\r\n\x1a\n" + b"test-image-data"
    upload = await auth_client.post(
        "/api/uploads",
        files={"files": ("class-photo.png", payload, "image/png")},
    )
    assert upload.status_code == 201
    file_id = upload.json()["files"][0]["id"]

    # Files are private by default, including direct URLs used by an anonymous visitor.
    anonymous = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    try:
        denied = await anonymous.get(f"/api/uploads/{file_id}/download")
        assert denied.status_code == 403
    finally:
        await anonymous.aclose()

    allowed = await auth_client.get(f"/api/uploads/{file_id}/download")
    assert allowed.status_code == 200
    assert allowed.content == payload

    bad_extension = await auth_client.post(
        "/api/uploads",
        files={"files": ("payload.exe", b"not allowed", "application/octet-stream")},
    )
    assert bad_extension.status_code == 400

    bad_signature = await auth_client.post(
        "/api/uploads",
        files={"files": ("not-really.png", b"not a png file", "image/png")},
    )
    assert bad_signature.status_code == 400
    assert len(list(Path(test_upload_dir).glob("*.png"))) == 1

    removed = await auth_client.delete(f"/api/uploads/admin/{file_id}")
    assert removed.status_code == 200


@pytest.mark.asyncio
async def test_non_editor_session_cannot_download_private_upload(client: AsyncClient, test_session_factory):
    file_id = uuid4()
    async with test_session_factory() as db:
        db.add(User(
            username="viewer",
            password_hash=hash_password("ViewerPass123!"),
            display_name="Viewer",
            role="VIEWER",
            is_active=True,
        ))
        db.add(StoredFile(
            id=file_id,
            storage_key=f"{file_id}.txt",
            original_filename="private.txt",
            display_filename="private.txt",
            mime_type="text/plain",
            extension=".txt",
            file_size=5,
            sha256_checksum="0" * 64,
            is_public=False,
        ))
        await db.commit()

    login = await client.post("/api/auth/login", json={"username": "viewer", "password": "ViewerPass123!"})
    assert login.status_code == 200
    response = await client.get(f"/api/uploads/{file_id}/download")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_upload_commit_failure_removes_file_and_metadata(
    auth_client: AsyncClient, test_session_factory, test_upload_dir, monkeypatch
):
    payload = b"\x89PNG\r\n\x1a\n" + b"test-image-data"

    async def fail_commit(_session):
        raise RuntimeError("injected commit failure")

    monkeypatch.setattr(AsyncSession, "commit", fail_commit)

    with pytest.raises(RuntimeError, match="injected commit failure"):
        await auth_client.post(
            "/api/uploads",
            files={"files": ("commit-failure.png", payload, "image/png")},
        )

    assert list(Path(test_upload_dir).iterdir()) == []
    async with test_session_factory() as db:
        count = await db.scalar(select(func.count(StoredFile.id)))
    assert count == 0
