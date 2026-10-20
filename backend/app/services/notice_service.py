"""Service functions for notice CRUD and querying."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import sanitize_html
from app.models.notice import Notice
from app.models.notice_attachment import NoticeAttachment
from app.models.stored_file import StoredFile
from app.schemas.notice import NoticeCreate, NoticeUpdate
from app.utils.datetime_utils import get_db_now
from app.utils.slug import generate_unique_slug


def _base_notice_query():
    """Return a base select with eager-loaded relationships."""
    return (
        select(Notice)
        .options(
            selectinload(Notice.author),
            selectinload(Notice.cover_image),
            selectinload(Notice.attachments).selectinload(NoticeAttachment.file),
        )
    )


async def get_public_notices(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    category: str | None = None,
    important_only: bool = False,
) -> tuple[list[Notice], int]:
    """Fetch published notices visible to the public.

    Includes PUBLISHED notices where published_at <= now and not expired.
    Also auto-publishes SCHEDULED notices whose published_at has arrived.
    Orders by is_pinned DESC, published_at DESC.
    """
    now = get_db_now(db)

    await publish_due_notices(db, now)

    # Build the public query
    conditions = [
        Notice.status == "PUBLISHED",
        Notice.published_at <= now,
        or_(Notice.expires_at.is_(None), Notice.expires_at > now),
    ]

    if search:
        like_pattern = f"%{search}%"
        conditions.append(
            or_(
                Notice.title.ilike(like_pattern),
                Notice.excerpt.ilike(like_pattern),
            )
        )

    if category:
        conditions.append(Notice.category == category)

    if important_only:
        conditions.append(Notice.is_important.is_(True))

    # Count total
    count_stmt = select(func.count(Notice.id)).where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    stmt = (
        _base_notice_query()
        .where(*conditions)
        .order_by(Notice.is_pinned.desc(), Notice.published_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    notices = list(result.scalars().unique().all())

    await db.commit()
    return notices, total


async def get_public_notice_by_slug(
    db: AsyncSession,
    slug: str,
) -> Notice | None:
    """Fetch a single published notice by slug."""
    now = get_db_now(db)
    await publish_due_notices(db, now)
    stmt = (
        _base_notice_query()
        .where(
            Notice.slug == slug,
            Notice.status == "PUBLISHED",
            Notice.published_at <= now,
            or_(Notice.expires_at.is_(None), Notice.expires_at > now),
        )
    )
    result = await db.execute(stmt)
    return result.scalars().unique().one_or_none()


async def publish_due_notices(db: AsyncSession, now: datetime | None = None) -> None:
    """Persist due scheduled notices before serving any public notice query."""
    now = now or get_db_now(db)
    result = await db.execute(
        select(Notice).where(Notice.status == "SCHEDULED", Notice.published_at <= now)
    )
    for notice in result.scalars().all():
        notice.status = "PUBLISHED"
    await db.flush()


async def get_admin_notices(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
) -> tuple[list[Notice], int]:
    """Fetch all notices for admin views with optional filters."""
    conditions: list = []

    if search:
        like_pattern = f"%{search}%"
        conditions.append(
            or_(
                Notice.title.ilike(like_pattern),
                Notice.excerpt.ilike(like_pattern),
            )
        )

    if category:
        conditions.append(Notice.category == category)

    if status:
        conditions.append(Notice.status == status)

    count_stmt = select(func.count(Notice.id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = _base_notice_query()
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = (
        stmt
        .order_by(Notice.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    notices = list(result.scalars().unique().all())

    return notices, total


async def create_notice(
    db: AsyncSession,
    data: NoticeCreate,
    author_id: UUID,
) -> Notice:
    """Create a new notice with sanitised HTML body and unique slug."""
    now = get_db_now(db)
    if data.status == "SCHEDULED" and data.published_at and _utc(data.published_at) <= _utc(now):
        raise ValueError("Scheduled publication time must be in the future")
    file_ids = list(data.attachment_ids)
    if len(file_ids) != len(set(file_ids)):
        raise ValueError("A file cannot be attached to a notice more than once")
    if data.cover_image_id:
        file_ids.append(data.cover_image_id)
    files = await _get_files(db, file_ids)

    slug = await generate_unique_slug(data.title, Notice, db)
    sanitized_body = sanitize_html(data.body)

    published_at = data.published_at

    if data.status == "PUBLISHED" and published_at is None:
        published_at = now
    if data.status in {"PUBLISHED", "SCHEDULED"} and data.expires_at and published_at and _utc(data.expires_at) <= _utc(published_at):
        raise ValueError("Expiry must be later than the publication time")
    if data.cover_image_id and not files[data.cover_image_id].mime_type.startswith("image/"):
        raise ValueError("Notice cover image must be an image upload")

    notice = Notice(
        slug=slug,
        title=data.title,
        excerpt=data.excerpt,
        body=sanitized_body,
        category=data.category,
        status=data.status,
        is_pinned=data.is_pinned,
        is_important=data.is_important,
        cover_image_id=data.cover_image_id,
        external_url=data.external_url,
        author_id=author_id,
        published_at=published_at,
        expires_at=data.expires_at,
    )
    db.add(notice)
    await db.flush()

    # Attach files
    if data.attachment_ids:
        for order, file_id in enumerate(data.attachment_ids):
            stored_file = files[file_id]
            attachment_type = "document"
            if stored_file and stored_file.mime_type.startswith("image/"):
                attachment_type = "image"

            attachment = NoticeAttachment(
                notice_id=notice.id,
                file_id=file_id,
                attachment_type=attachment_type,
                display_order=order,
            )
            db.add(attachment)

    await db.commit()

    # Re-fetch with relationships
    stmt = _base_notice_query().where(Notice.id == notice.id)
    result = await db.execute(stmt)
    return result.scalars().unique().one()


async def update_notice(
    db: AsyncSession,
    notice_id: UUID,
    data: NoticeUpdate,
) -> Notice:
    """Update an existing notice."""
    stmt = _base_notice_query().where(Notice.id == notice_id)
    result = await db.execute(stmt)
    notice = result.scalars().unique().one_or_none()

    if notice is None:
        raise ValueError("Notice not found")

    update_data = data.model_dump(exclude_unset=True)

    now = get_db_now(db)
    if update_data.get("status") == "SCHEDULED":
        scheduled_at = update_data.get("published_at", notice.published_at)
        if scheduled_at is None or _utc(scheduled_at) <= _utc(now):
            raise ValueError("Scheduled publication time must be in the future")
    effective_published_at = update_data.get("published_at", notice.published_at)
    effective_expires_at = update_data.get("expires_at", notice.expires_at)
    if effective_published_at and effective_expires_at and _utc(effective_expires_at) <= _utc(effective_published_at):
        raise ValueError("Expiry must be later than the publication time")

    attachment_ids = update_data.get("attachment_ids")
    file_ids = list(attachment_ids or [])
    if len(file_ids) != len(set(file_ids)):
        raise ValueError("A file cannot be attached to a notice more than once")
    cover_id = update_data.get("cover_image_id", notice.cover_image_id)
    if cover_id:
        file_ids.append(cover_id)
    files = await _get_files(db, file_ids)
    if cover_id and not files[cover_id].mime_type.startswith("image/"):
        raise ValueError("Notice cover image must be an image upload")

    if "body" in update_data and update_data["body"] is not None:
        update_data["body"] = sanitize_html(update_data["body"])

    if "title" in update_data and update_data["title"] is not None:
        update_data["slug"] = await generate_unique_slug(
            update_data["title"], Notice, db, existing_id=str(notice.id)
        )

    # Handle status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "PUBLISHED" and notice.published_at is None and "published_at" not in update_data:
            update_data["published_at"] = now

    final_published_at = update_data.get("published_at", notice.published_at)
    final_expires_at = update_data.get("expires_at", notice.expires_at)
    if final_published_at and final_expires_at and _utc(final_expires_at) <= _utc(final_published_at):
        raise ValueError("Expiry must be later than the publication time")

    # Handle attachment_ids separately
    attachment_ids = update_data.pop("attachment_ids", None)

    for key, value in update_data.items():
        setattr(notice, key, value)

    if attachment_ids is not None:
        # Remove existing attachments
        for att in list(notice.attachments):
            await db.delete(att)
        await db.flush()

        # Add new attachments
        for order, file_id in enumerate(attachment_ids):
            stored_file = files[file_id]
            attachment_type = "document"
            if stored_file and stored_file.mime_type.startswith("image/"):
                attachment_type = "image"

            attachment = NoticeAttachment(
                notice_id=notice.id,
                file_id=file_id,
                attachment_type=attachment_type,
                display_order=order,
            )
            db.add(attachment)

    await db.commit()

    # Re-fetch
    stmt = _base_notice_query().where(Notice.id == notice.id)
    result = await db.execute(stmt)
    return result.scalars().unique().one()


async def delete_notice(
    db: AsyncSession,
    notice_id: UUID,
) -> None:
    """Delete a notice and its attachments."""
    stmt = select(Notice).where(Notice.id == notice_id)
    result = await db.execute(stmt)
    notice = result.scalar_one_or_none()

    if notice is None:
        raise ValueError("Notice not found")

    await db.delete(notice)
    await db.commit()


async def _get_files(db: AsyncSession, file_ids: list[UUID]) -> dict[UUID, StoredFile]:
    """Fetch referenced files in one query and fail cleanly on missing IDs."""
    if not file_ids:
        return {}
    result = await db.execute(select(StoredFile).where(StoredFile.id.in_(set(file_ids))))
    files = {stored_file.id: stored_file for stored_file in result.scalars().all()}
    missing = set(file_ids) - files.keys()
    if missing:
        raise ValueError("One or more referenced upload files do not exist")
    return files


def _utc(value: datetime) -> datetime:
    from datetime import timezone
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
