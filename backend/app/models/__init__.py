"""Import all models so Alembic can discover them."""

from app.models.user import User
from app.models.session import Session
from app.models.login_attempt import LoginAttempt
from app.models.stored_file import StoredFile
from app.models.notice import Notice
from app.models.notice_attachment import NoticeAttachment
from app.models.document import Document
from app.models.inquiry import Inquiry
from app.models.inquiry_rate_limit import InquiryRateLimit
from app.models.gallery_item import GalleryItem

__all__ = [
    "User",
    "Session",
    "LoginAttempt",
    "StoredFile",
    "Notice",
    "NoticeAttachment",
    "Document",
    "Inquiry",
    "InquiryRateLimit",
    "GalleryItem",
]
