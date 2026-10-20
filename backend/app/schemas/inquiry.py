"""Pydantic schemas for inquiry (contact/admission form) endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class InquiryCreate(BaseModel):
    """Request body for submitting a contact inquiry."""

    parent_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=7, max_length=20)
    email: EmailStr | None = None
    child_age: str | None = Field(None, max_length=50)
    program: str | None = Field(None, max_length=100)
    message: str | None = Field(None, max_length=2000)
    website: str = Field("", max_length=200)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Ensure phone contains only digits, spaces, dashes, plus, and parens."""
        cleaned = v.strip()
        allowed = set("0123456789+-() ")
        if not all(c in allowed for c in cleaned):
            raise ValueError("Phone number contains invalid characters")
        return cleaned


class InquiryResponse(BaseModel):
    """Full inquiry representation."""

    id: UUID
    parent_name: str
    phone: str
    email: str | None = None
    child_age: str | None = None
    program: str | None = None
    message: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InquiryListResponse(BaseModel):
    """Paginated list of inquiries."""

    items: list[InquiryResponse]
    total: int
    page: int
    page_size: int
