"""Pydantic schemas for document endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

DOCUMENT_STATUSES = {"DRAFT", "SCHEDULED", "PUBLISHED", "UNPUBLISHED", "ARCHIVED"}
DOCUMENT_CATEGORIES = {"Forms", "School Circulars", "Parent Guidelines", "Event Documents", "Learning Resources", "Other Documents"}


class DocumentCreate(BaseModel):
    """Request body to create a document."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    category: str = Field(..., min_length=1, max_length=50)
    file_id: UUID
    status: str = "DRAFT"
    published_at: datetime | None = None
    expires_at: datetime | None = None

    @field_validator("category")
    @classmethod
    def valid_category(cls, value: str) -> str:
        if value not in DOCUMENT_CATEGORIES:
            raise ValueError("Unsupported document category")
        return value

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        if value not in DOCUMENT_STATUSES:
            raise ValueError("Unsupported document status")
        return value

    @model_validator(mode="after")
    def scheduled_needs_publication_time(self):
        if self.status == "SCHEDULED" and self.published_at is None:
            raise ValueError("Scheduled documents need a publication date and time")
        return self


class DocumentUpdate(BaseModel):
    """Request body to update a document. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(None, min_length=1, max_length=50)
    file_id: UUID | None = None
    status: str | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None

    @field_validator("category")
    @classmethod
    def valid_category(cls, value: str | None) -> str | None:
        if value is not None and value not in DOCUMENT_CATEGORIES:
            raise ValueError("Unsupported document category")
        return value

    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str | None) -> str | None:
        if value is not None and value not in DOCUMENT_STATUSES:
            raise ValueError("Unsupported document status")
        return value

    @model_validator(mode="after")
    def scheduled_needs_publication_time(self):
        if self.status == "SCHEDULED" and self.published_at is None:
            raise ValueError("Scheduled documents need a publication date and time")
        return self


class DocumentFileInfo(BaseModel):
    """Embedded file info in a document response."""

    id: UUID
    original_filename: str
    mime_type: str
    extension: str
    file_size: int

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    """Full document representation."""

    id: UUID
    title: str
    description: str
    category: str
    status: str
    file: DocumentFileInfo
    download_url: str
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
