"""Admin dashboard and overview metrics routes."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.notices import _build_notice_response
from app.core.dependencies import get_db, require_admin
from app.models.document import Document
from app.models.inquiry import Inquiry
from app.models.notice import Notice
from app.models.stored_file import StoredFile
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.schemas.inquiry import InquiryResponse
from app.schemas.upload import UploadResponse
from app.services.notice_service import _base_notice_query, publish_due_notices
from app.utils.datetime_utils import get_db_now

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
) -> DashboardResponse:
    """Return actual database metrics and recent items for the administrative dashboard."""
    now = get_db_now(db)
    await publish_due_notices(db, now)
    due_documents = await db.execute(
        select(Document).where(Document.status == "SCHEDULED", Document.published_at <= now)
    )
    for document in due_documents.scalars().all():
        document.status = "PUBLISHED"
    await db.commit()

    # 1. Counts
    pub_notices_stmt = select(func.count(Notice.id)).where(
        Notice.status == "PUBLISHED",
        Notice.published_at <= now,
        (Notice.expires_at.is_(None) | (Notice.expires_at > now)),
    )
    published_notices = (await db.execute(pub_notices_stmt)).scalar_one()

    draft_notices_stmt = select(func.count(Notice.id)).where(Notice.status == "DRAFT")
    draft_notices = (await db.execute(draft_notices_stmt)).scalar_one()

    sched_notices_stmt = select(func.count(Notice.id)).where(
        Notice.status == "SCHEDULED", Notice.published_at > now
    )
    scheduled_notices = (await db.execute(sched_notices_stmt)).scalar_one()

    pub_docs_stmt = select(func.count(Document.id)).where(
        Document.status == "PUBLISHED",
        Document.published_at <= now,
        (Document.expires_at.is_(None) | (Document.expires_at > now)),
    )
    published_documents = (await db.execute(pub_docs_stmt)).scalar_one()

    inquiries_stmt = select(func.count(Inquiry.id))
    total_inquiries = (await db.execute(inquiries_stmt)).scalar_one()

    unread_inquiries_stmt = select(func.count(Inquiry.id)).where(Inquiry.status == "NEW")
    unread_inquiries = (await db.execute(unread_inquiries_stmt)).scalar_one()

    # 2. Recent notices
    recent_notices_stmt = _base_notice_query().order_by(Notice.created_at.desc()).limit(5)
    recent_notices_raw = (await db.execute(recent_notices_stmt)).scalars().unique().all()
    recent_notices = [_build_notice_response(n) for n in recent_notices_raw]

    # 3. Recent uploads
    recent_files_stmt = select(StoredFile).order_by(StoredFile.created_at.desc()).limit(5)
    recent_files_raw = (await db.execute(recent_files_stmt)).scalars().all()
    recent_uploads = [
        UploadResponse(
            id=f.id,
            original_filename=f.original_filename,
            display_filename=f.display_filename,
            mime_type=f.mime_type,
            extension=f.extension,
            file_size=f.file_size,
            download_url=f"/api/uploads/{f.id}/download",
        )
        for f in recent_files_raw
    ]

    # 4. Recent inquiries
    recent_inq_stmt = select(Inquiry).order_by(Inquiry.created_at.desc()).limit(5)
    recent_inq_raw = (await db.execute(recent_inq_stmt)).scalars().all()
    recent_inquiries = [InquiryResponse.model_validate(i) for i in recent_inq_raw]

    return DashboardResponse(
        published_notices=published_notices,
        draft_notices=draft_notices,
        scheduled_notices=scheduled_notices,
        published_documents=published_documents,
        total_inquiries=total_inquiries,
        unread_inquiries=unread_inquiries,
        recent_notices=recent_notices,
        recent_uploads=recent_uploads,
        recent_inquiries=recent_inquiries,
    )
