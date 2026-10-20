"""Service functions for document CRUD and querying."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.models.stored_file import StoredFile
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.utils.datetime_utils import get_db_now


def _base_document_query():
    """Return a base select with eager-loaded file relationship."""
    return select(Document).options(
        selectinload(Document.file),
        selectinload(Document.uploader),
    )


async def get_public_documents(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    category: str | None = None,
    file_type: str | None = None,
    sort: str = "newest",
) -> tuple[list[Document], int]:
    """Fetch published, non-expired documents for public view."""
    now = get_db_now(db)

    due_result = await db.execute(select(Document).where(
        Document.status == "SCHEDULED", Document.published_at <= now
    ))
    due_documents = list(due_result.scalars().all())
    for document in due_documents:
        document.status = "PUBLISHED"
    if due_documents:
        await db.commit()

    conditions = [
        Document.status == "PUBLISHED",
        Document.published_at <= now,
        or_(Document.expires_at.is_(None), Document.expires_at > now),
    ]

    if search:
        like_pattern = f"%{search}%"
        conditions.append(
            or_(
                Document.title.ilike(like_pattern),
                Document.description.ilike(like_pattern),
            )
        )

    if category:
        conditions.append(Document.category == category)

    if file_type:
        file_type = file_type.lower()
        type_map: dict[str, set[str]] = {
            "pdf": {".pdf"},
            "doc": {".doc"},
            "docx": {".docx"},
            "jpg": {".jpg", ".jpeg"},
            "jpeg": {".jpg", ".jpeg"},
            "png": {".png"},
            "webp": {".webp"},
            "word": {".doc", ".docx"},
            "excel": {".xls", ".xlsx"},
            "powerpoint": {".ppt", ".pptx"},
            "image": {".jpg", ".jpeg", ".png", ".webp"},
        }
        allowed_exts = type_map.get(file_type)
        if allowed_exts:
            conditions.append(Document.file.has(StoredFile.extension.in_(allowed_exts)))

    # Count
    count_stmt = select(func.count(Document.id)).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    # Query with ordering
    stmt = _base_document_query().where(*conditions)

    if sort == "oldest":
        stmt = stmt.order_by(Document.published_at.asc())
    elif sort == "title":
        stmt = stmt.order_by(Document.title.asc())
    elif sort == "type":
        stmt = stmt.join(Document.file).order_by(StoredFile.extension.asc())
    else:  # newest (default)
        stmt = stmt.order_by(Document.published_at.desc().nullslast())

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    documents = list(result.scalars().unique().all())

    return documents, total


async def get_admin_documents(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
) -> tuple[list[Document], int]:
    """Fetch all documents for admin view with optional filters."""
    conditions: list = []

    if search:
        like_pattern = f"%{search}%"
        conditions.append(
            or_(
                Document.title.ilike(like_pattern),
                Document.description.ilike(like_pattern),
            )
        )

    if category:
        conditions.append(Document.category == category)

    if status:
        conditions.append(Document.status == status)

    count_stmt = select(func.count(Document.id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = _base_document_query()
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = (
        stmt.order_by(Document.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(stmt)
    documents = list(result.scalars().unique().all())

    return documents, total


async def create_document(
    db: AsyncSession,
    data: DocumentCreate,
    uploader_id: UUID,
) -> Document:
    """Create a new document record."""
    now = get_db_now(db)
    file = await db.get(StoredFile, data.file_id)
    if file is None:
        raise ValueError("Referenced upload file does not exist")
    published_at = data.published_at

    if data.status == "SCHEDULED" and published_at and _utc(published_at) <= _utc(now):
        raise ValueError("Scheduled publication time must be in the future")
    if published_at and data.expires_at and _utc(data.expires_at) <= _utc(published_at):
        raise ValueError("Expiry must be later than the publication time")

    if data.status == "PUBLISHED" and published_at is None:
        published_at = now
    if data.status in {"PUBLISHED", "SCHEDULED"} and data.expires_at and published_at and _utc(data.expires_at) <= _utc(published_at):
        raise ValueError("Expiry must be later than the publication time")

    document = Document(
        title=data.title,
        description=data.description,
        category=data.category,
        file_id=data.file_id,
        status=data.status,
        uploader_id=uploader_id,
        published_at=published_at,
        expires_at=data.expires_at,
    )
    db.add(document)
    await db.commit()

    # Re-fetch with relationships
    stmt = _base_document_query().where(Document.id == document.id)
    result = await db.execute(stmt)
    return result.scalars().unique().one()


async def update_document(
    db: AsyncSession,
    document_id: UUID,
    data: DocumentUpdate,
) -> Document:
    """Update an existing document."""
    # Serialize concurrent edits to one document on PostgreSQL.
    stmt = _base_document_query().where(Document.id == document_id).with_for_update()
    result = await db.execute(stmt)
    document = result.scalars().unique().one_or_none()

    if document is None:
        raise ValueError("Document not found")

    update_data = data.model_dump(exclude_unset=True)

    now = get_db_now(db)
    if "file_id" in update_data and update_data["file_id"] is not None:
        if await db.get(StoredFile, update_data["file_id"]) is None:
            raise ValueError("Referenced upload file does not exist")
    if update_data.get("status") == "SCHEDULED":
        scheduled_at = update_data.get("published_at", document.published_at)
        if scheduled_at is None or _utc(scheduled_at) <= _utc(now):
            raise ValueError("Scheduled publication time must be in the future")
    effective_published_at = update_data.get("published_at", document.published_at)
    effective_expires_at = update_data.get("expires_at", document.expires_at)
    if effective_published_at and effective_expires_at and _utc(effective_expires_at) <= _utc(effective_published_at):
        raise ValueError("Expiry must be later than the publication time")

    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "PUBLISHED" and document.published_at is None and "published_at" not in update_data:
            update_data["published_at"] = now

    for key, value in update_data.items():
        setattr(document, key, value)

    await db.commit()

    # Re-fetch
    stmt = _base_document_query().where(Document.id == document.id)
    result = await db.execute(stmt)
    return result.scalars().unique().one()


async def delete_document(
    db: AsyncSession,
    document_id: UUID,
) -> None:
    """Delete a document record (does not delete the underlying file)."""
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if document is None:
        raise ValueError("Document not found")

    await db.delete(document)
    await db.commit()


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
