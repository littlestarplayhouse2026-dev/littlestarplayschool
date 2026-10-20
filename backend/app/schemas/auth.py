"""Pydantic schemas for authentication endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Request body for POST /api/auth/login."""

    username: str | None = None
    password: str = Field(..., min_length=1, max_length=128)

    @property
    def account_identifier(self) -> str:
        ident = (self.username or "").strip()
        return ident


class ChangePasswordRequest(BaseModel):
    """Request body for POST /api/auth/change-password."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=12, max_length=128)


class UserResponse(BaseModel):
    """Public representation of a User."""

    id: UUID
    username: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response after successful login or GET /api/auth/me."""

    user: UserResponse
    csrf_token: str


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
