"""Pydantic schemas for the admin dashboard."""

from pydantic import BaseModel

from app.schemas.inquiry import InquiryResponse
from app.schemas.notice import NoticeResponse
from app.schemas.upload import UploadResponse


class DashboardResponse(BaseModel):
    """Aggregate metrics and recent activity for the admin dashboard."""

    published_notices: int
    draft_notices: int
    scheduled_notices: int
    published_documents: int
    total_inquiries: int
    unread_inquiries: int
    recent_notices: list[NoticeResponse]
    recent_uploads: list[UploadResponse]
    recent_inquiries: list[InquiryResponse] = []
