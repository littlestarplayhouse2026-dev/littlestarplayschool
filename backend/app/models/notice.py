"""Notice ORM model for school announcements and news."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Notice(Base):
    """A notice/announcement published by the school."""

    __tablename__ = "notices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(
        String(280), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)  # sanitized HTML
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # Important, General, Events, Holidays, Documents
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="DRAFT", index=True
    )  # DRAFT, SCHEDULED, PUBLISHED, UNPUBLISHED, ARCHIVED
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_image_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("stored_files.id", ondelete="SET NULL")
    )
    external_url: Mapped[str | None] = mapped_column(String(2048))
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    author: Mapped["User"] = relationship("User")  # type: ignore[name-defined]  # noqa: F821
    cover_image: Mapped["StoredFile | None"] = relationship("StoredFile")  # type: ignore[name-defined]  # noqa: F821
    attachments: Mapped[list["NoticeAttachment"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "NoticeAttachment",
        back_populates="notice",
        cascade="all, delete-orphan",
        order_by="NoticeAttachment.display_order",
    )
