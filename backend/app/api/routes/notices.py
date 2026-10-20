"""Notice routes for public visitors and authenticated administrators."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_editor_or_admin, verify_csrf
from app.models.notice import Notice
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.notice import (
    AttachmentResponse,
    NoticeAuthorResponse,
    NoticeCreate,
    NoticeListResponse,
    NoticePublicResponse,
    NoticePublicListResponse,
    NoticePublicAuthorResponse,
    NoticeResponse,
    NoticeUpdate,
)
from app.services import notice_service
from app.utils.datetime_utils import get_db_now

router = APIRouter(prefix="/notices", tags=["Notices"])


def _build_notice_response(notice: Notice) -> NoticeResponse:
    """Helper to convert a Notice model with relationships into NoticeResponse."""
    attachments: list[AttachmentResponse] = []
    if notice.attachments:
        for att in notice.attachments:
            orig_name = att.file.original_filename if att.file else "attachment"
            mime = att.file.mime_type if att.file else "application/octet-stream"
            size = att.file.file_size if att.file else 0
            attachments.append(
                AttachmentResponse(
                    id=att.id,
                    file_id=att.file_id,
                    filename=orig_name,
                    mime_type=mime,
                    size=size,
                    type=att.attachment_type,
                    caption=att.caption,
                    download_url=f"/api/uploads/{att.file_id}/download",
                )
            )

    cover_url = f"/api/uploads/{notice.cover_image_id}/download" if notice.cover_image_id else None

    return NoticeResponse(
        id=notice.id,
        slug=notice.slug,
        title=notice.title,
        excerpt=notice.excerpt,
        body=notice.body,
        category=notice.category,
        status=notice.status,
        is_pinned=notice.is_pinned,
        is_important=notice.is_important,
        cover_image_id=notice.cover_image_id,
        cover_image_url=cover_url,
        external_url=notice.external_url,
        author=NoticeAuthorResponse(
            id=notice.author.id,
            display_name=notice.author.display_name,
        ),
        attachments=attachments,
        created_at=notice.created_at,
        updated_at=notice.updated_at,
        published_at=notice.published_at,
        expires_at=notice.expires_at,
    )


def _build_public_notice_response(notice: Notice) -> NoticePublicResponse:
    """Helper to convert a Notice into NoticePublicResponse."""
    full = _build_notice_response(notice)
    return NoticePublicResponse(
        id=full.id,
        slug=full.slug,
        title=full.title,
        excerpt=full.excerpt,
        body=full.body,
        category=full.category,
        is_pinned=full.is_pinned,
        is_important=full.is_important,
        cover_image_url=full.cover_image_url,
        external_url=full.external_url,
        author=NoticePublicAuthorResponse(display_name=full.author.display_name),
        attachments=full.attachments,
        published_at=full.published_at,
    )


# ─── Public Endpoints ─────────────────────────────────────────────

@router.get("", response_model=NoticePublicListResponse)
async def list_public_notices(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    search: str | None = None,
    category: str | None = None,
    important_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> NoticePublicListResponse:
    """Public list of published, active notices with pagination and search."""
    notices, total = await notice_service.get_public_notices(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        important_only=important_only,
    )
    items = [_build_public_notice_response(n) for n in notices]
    return NoticePublicListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/admin/list/all", response_model=NoticeListResponse)
async def list_admin_notices(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
) -> NoticeListResponse:
    """Protected list of all notices for administrators (drafts, scheduled, published)."""
    notices, total = await notice_service.get_admin_notices(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        status=status,
    )
    items = [_build_notice_response(n) for n in notices]
    return NoticeListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/admin/detail/{notice_id}", response_model=NoticeResponse)
async def get_admin_notice_detail(
    notice_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
) -> NoticeResponse:
    """Protected single notice fetch by ID for editor (returns drafts, scheduled, etc.)."""
    stmt = notice_service._base_notice_query().where(Notice.id == notice_id)
    result = await db.execute(stmt)
    notice = result.scalars().unique().one_or_none()
    if notice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found",
        )
    return _build_notice_response(notice)


@router.get("/{id_or_slug}", response_model=NoticePublicResponse)
async def get_notice(
    id_or_slug: str,
    db: AsyncSession = Depends(get_db),
) -> NoticePublicResponse:
    """Public single notice fetch by ID or slug."""
    # Try by slug first
    notice = await notice_service.get_public_notice_by_slug(db, id_or_slug)

    # If not found and is valid UUID, try by ID
    if notice is None:
        try:
            val_uuid = UUID(id_or_slug)
            now = get_db_now(db)
            await notice_service.publish_due_notices(db, now)
            stmt = notice_service._base_notice_query().where(
                Notice.id == val_uuid,
                Notice.status == "PUBLISHED",
                Notice.published_at <= now,
                or_(Notice.expires_at.is_(None), Notice.expires_at > now),
            )
            result = await db.execute(stmt)
            notice = result.scalars().unique().one_or_none()
        except ValueError:
            pass

    if notice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found",
        )

    return _build_public_notice_response(notice)


# ─── Admin Endpoints ──────────────────────────────────────────────

@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def create_notice(
    data: NoticeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> NoticeResponse:
    """Create a new notice."""
    try:
        notice = await notice_service.create_notice(db, data, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _build_notice_response(notice)


@router.put("/{notice_id}", response_model=NoticeResponse)
async def update_notice(
    notice_id: UUID,
    data: NoticeUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> NoticeResponse:
    """Update an existing notice."""
    try:
        notice = await notice_service.update_notice(db, notice_id, data)
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if str(exc) == "Notice not found" else 422
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return _build_notice_response(notice)


@router.delete("/{notice_id}", response_model=MessageResponse)
async def delete_notice(
    notice_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> MessageResponse:
    """Delete a notice."""
    await notice_service.delete_notice(db, notice_id)
    return MessageResponse(message="Notice deleted successfully")

