"""Gallery API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GalleryItemResponse(BaseModel):
    id: UUID
    file_id: UUID
    caption: str
    image_url: str
    created_at: datetime


class GalleryListResponse(BaseModel):
    items: list[GalleryItemResponse]
