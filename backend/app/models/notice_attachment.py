"""NoticeAttachment ORM model linking notices to uploaded files."""

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NoticeAttachment(Base):
    """Joins a notice to one or more uploaded files (documents or images)."""

    __tablename__ = "notice_attachments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    notice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("stored_files.id", ondelete="CASCADE"), nullable=False
    )
    attachment_type: Mapped[str] = mapped_column(
        String(20), default="document"
    )  # document, image
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    caption: Mapped[str | None] = mapped_column(String(500))

    notice: Mapped["Notice"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Notice", back_populates="attachments"
    )
    file: Mapped["StoredFile"] = relationship("StoredFile")  # type: ignore[name-defined]  # noqa: F821
