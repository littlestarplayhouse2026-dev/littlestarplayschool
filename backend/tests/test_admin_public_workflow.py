import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_admin_to_public_content_workflow(auth_client: AsyncClient):
    # Public enquiry is stored and appears in the protected messages list.
    inquiry = await auth_client.post(
        "/api/inquiries",
        json={"parent_name": "Test Parent", "phone": "+977 9800000000", "message": "Test only"},
    )
    assert inquiry.status_code == 201
    messages = await auth_client.get("/api/inquiries/admin/list/all")
    assert any(row["id"] == inquiry.json()["id"] for row in messages.json()["items"])

    # Draft notice is private, then becomes public only after its status is changed.
    draft = await auth_client.post(
        "/api/notices",
        json={"title": "Workflow Test Notice", "excerpt": "Test", "body": "<p>Test</p>", "category": "General", "status": "DRAFT"},
    )
    assert draft.status_code == 201
    notice_id = draft.json()["id"]
    public_notices = await auth_client.get("/api/notices")
    assert not any(row["id"] == notice_id for row in public_notices.json()["items"])
    published_notice = await auth_client.put(f"/api/notices/{notice_id}", json={"status": "PUBLISHED"})
    assert published_notice.status_code == 200
    public_notices = await auth_client.get("/api/notices")
    assert any(row["id"] == notice_id for row in public_notices.json()["items"])
    dashboard_after_notice = await auth_client.get("/api/admin/dashboard")
    assert dashboard_after_notice.json()["published_notices"] >= 1

    # Uploaded bytes become available through the public library only while the
    # associated document is published, and go private again when unpublished.
    upload = await auth_client.post(
        "/api/uploads",
        files={"files": ("workflow.txt", b"test document body", "text/plain")},
    )
    assert upload.status_code == 201
    file_id = upload.json()["files"][0]["id"]
    document = await auth_client.post(
        "/api/documents",
        json={"title": "Workflow Test Resource", "description": "Test only", "category": "Other Documents", "file_id": file_id, "status": "PUBLISHED"},
    )
    assert document.status_code == 201
    document_id = document.json()["id"]
    resources = await auth_client.get("/api/documents")
    assert any(row["id"] == document_id for row in resources.json()["items"])
    dashboard_after_document = await auth_client.get("/api/admin/dashboard")
    assert dashboard_after_document.json()["published_documents"] >= 1
    downloaded = await auth_client.get(f"/api/uploads/{file_id}/download")
    assert downloaded.status_code == 200
    assert downloaded.content == b"test document body"

    unpublished = await auth_client.put(f"/api/documents/{document_id}", json={"status": "DRAFT"})
    assert unpublished.status_code == 200
    resources = await auth_client.get("/api/documents")
    assert not any(row["id"] == document_id for row in resources.json()["items"])
    dashboard_after_unpublish = await auth_client.get("/api/admin/dashboard")
    assert dashboard_after_unpublish.json()["published_documents"] == 0
    anonymous = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    try:
        denied = await anonymous.get(f"/api/uploads/{file_id}/download")
        assert denied.status_code == 403
    finally:
        await anonymous.aclose()

    logout = await auth_client.post("/api/auth/logout")
    assert logout.status_code == 200
    protected = await auth_client.get("/api/admin/dashboard")
    assert protected.status_code == 401
