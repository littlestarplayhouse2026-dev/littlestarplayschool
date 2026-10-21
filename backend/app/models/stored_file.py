"""StoredFile ORM model for uploaded file metadata."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StoredFile(Base):
    """Metadata record for an uploaded file stored on disk."""

    __tablename__ = "stored_files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    storage_key: Mapped[str] = mapped_column(
        String(512), unique=True, nullable=False
    )
    storage_backend: Mapped[str] = mapped_column(String(20), nullable=False, default="local")
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    display_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    extension: Mapped[str] = mapped_column(String(20), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    uploader_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    uploader: Mapped["User | None"] = relationship("User")  # type: ignore[name-defined]  # noqa: F821
