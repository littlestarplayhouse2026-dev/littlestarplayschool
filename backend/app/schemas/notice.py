"""Pydantic schemas for notice endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_CATEGORIES = {"Important", "General", "Events", "Holidays", "Documents"}
ALLOWED_STATUSES = {"DRAFT", "SCHEDULED", "PUBLISHED", "UNPUBLISHED", "ARCHIVED"}


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


class AttachmentResponse(BaseModel):
    """A single attachment belonging to a notice."""

    id: UUID
    file_id: UUID
    filename: str
    mime_type: str
    size: int
    type: str  # document or image
    caption: str | None = None
    download_url: str

    model_config = {"from_attributes": True}


class NoticeCreate(BaseModel):
    """Request body to create a notice."""

    title: str = Field(..., min_length=1, max_length=255)
    excerpt: str = Field(..., min_length=1, max_length=1000)
    body: str = Field(..., max_length=50000)
    category: str
    status: str = "DRAFT"
    is_pinned: bool = False
    is_important: bool = False
    cover_image_id: UUID | None = None
    external_url: str | None = None
    attachment_ids: list[UUID] = Field(default_factory=list)
    published_at: datetime | None = None
    expires_at: datetime | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in ALLOWED_CATEGORIES:
            raise ValueError(f"category must be one of {ALLOWED_CATEGORIES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_STATUSES}")
        return v

    @field_validator("external_url")
    @classmethod
    def validate_external_url(cls, v: str | None) -> str | None:
        if v is not None and not v.strip().lower().startswith(("http://", "https://")):
            raise ValueError("external_url must start with http:// or https://")
        return v

    @model_validator(mode="after")
    def validate_publication_dates(self):
        if self.status == "SCHEDULED" and self.published_at is None:
            raise ValueError("Scheduled notices need a publication date and time")
        if self.published_at and self.expires_at and _utc(self.expires_at) <= _utc(self.published_at):
            raise ValueError("Expiry must be later than the publication time")
        return self


class NoticeUpdate(BaseModel):
    """Request body to update a notice. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    excerpt: str | None = Field(None, min_length=1, max_length=1000)
    body: str | None = Field(None, max_length=50000)
    category: str | None = None
    status: str | None = None
    is_pinned: bool | None = None
    is_important: bool | None = None
    cover_image_id: UUID | None = None
    external_url: str | None = None
    attachment_ids: list[UUID] | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        if v is not None and v not in ALLOWED_CATEGORIES:
            raise ValueError(f"category must be one of {ALLOWED_CATEGORIES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ALLOWED_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_STATUSES}")
        return v

    @field_validator("external_url")
    @classmethod
    def validate_external_url(cls, v: str | None) -> str | None:
        if v is not None and not v.strip().lower().startswith(("http://", "https://")):
            raise ValueError("external_url must start with http:// or https://")
        return v

    @model_validator(mode="after")
    def validate_publication_dates(self):
        if self.status == "SCHEDULED" and self.published_at is None:
            raise ValueError("Scheduled notices need a publication date and time")
        if self.published_at and self.expires_at and _utc(self.expires_at) <= _utc(self.published_at):
            raise ValueError("Expiry must be later than the publication time")
        return self


class NoticeAuthorResponse(BaseModel):
    """Embedded author info in a notice response."""

    id: UUID
    display_name: str

    model_config = {"from_attributes": True}


class NoticeResponse(BaseModel):
    """Full notice representation for admin views."""

    id: UUID
    slug: str
    title: str
    excerpt: str
    body: str
    category: str
    status: str
    is_pinned: bool
    is_important: bool
    cover_image_id: UUID | None = None
    cover_image_url: str | None = None
    external_url: str | None = None
    author: NoticeAuthorResponse
    attachments: list[AttachmentResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}


class NoticeListResponse(BaseModel):
    """Paginated list of notices."""

    items: list[NoticeResponse]
    total: int
    page: int
    page_size: int


class NoticePublicAuthorResponse(BaseModel):
    """Public author information without internal user IDs."""

    display_name: str


class NoticePublicResponse(BaseModel):
    """Public notice representation (omits admin-only fields)."""

    id: UUID
    slug: str
    title: str
    excerpt: str
    body: str
    category: str
    is_pinned: bool
    is_important: bool
    cover_image_url: str | None = None
    external_url: str | None = None
    author: "NoticePublicAuthorResponse"
    attachments: list[AttachmentResponse] = Field(default_factory=list)
    published_at: datetime | None = None

    model_config = {"from_attributes": True}


class NoticePublicListResponse(BaseModel):
    """Paginated public notices without internal management fields."""

    items: list[NoticePublicResponse]
    total: int
    page: int
    page_size: int
