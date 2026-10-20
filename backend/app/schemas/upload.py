"""Pydantic schemas for file upload endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Metadata for a single uploaded file."""

    id: UUID
    original_filename: str
    display_filename: str
    mime_type: str
    extension: str
    file_size: int
    download_url: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class UploadListResponse(BaseModel):
    """List of uploaded files."""

    files: list[UploadResponse]


class PaginatedUploadResponse(BaseModel):
    """Paginated list of uploaded files for the file manager."""

    items: list[UploadResponse]
    total: int
    page: int
    page_size: int
