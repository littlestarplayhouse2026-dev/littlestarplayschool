"""Upload and file download routes with strict access controls."""

from datetime import datetime, timezone
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db, require_editor_or_admin, verify_csrf
from app.core.security import hash_session_token
from app.models.document import Document
from app.models.gallery_item import GalleryItem
from app.models.notice import Notice
from app.models.notice_attachment import NoticeAttachment
from app.models.session import Session
from app.models.stored_file import StoredFile
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.upload import PaginatedUploadResponse, UploadListResponse, UploadResponse
from app.services.storage_service import StorageError, get_storage_service, get_storage_service_for_file
from app.utils.datetime_utils import get_db_now

router = APIRouter(prefix="/uploads", tags=["Uploads"])
logger = logging.getLogger(__name__)


def _storage_service():
    """Build the configured adapter, honoring test/deployment setting overrides."""
    return get_storage_service()


@router.post("", response_model=UploadListResponse, status_code=status.HTTP_201_CREATED)
async def upload_files(
    files: list[UploadFile],
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> UploadListResponse:
    """Upload one or more files. Validates extension, magic bytes, size limits."""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided in request",
        )

    uploaded: list[UploadResponse] = []
    saved_keys: list[tuple[object, str]] = []
    storage = _storage_service()
    try:
        for file in files:
            content_length = file.size
            if content_length and content_length > settings.max_upload_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File '{file.filename}' exceeds maximum allowed size of {settings.MAX_UPLOAD_MB} MB",
                )
            stored_file = await storage.save_file(
                file=file,
                uploader_id=user.id,
                is_public=False,
            )
            saved_keys.append((storage, stored_file.storage_key))
            db.add(stored_file)
            await db.flush()

            uploaded.append(
                UploadResponse(
                    id=stored_file.id,
                    original_filename=stored_file.original_filename,
                    display_filename=stored_file.display_filename,
                    mime_type=stored_file.mime_type,
                    extension=stored_file.extension,
                    file_size=stored_file.file_size,
                    download_url=f"/api/uploads/{stored_file.id}/download",
                    created_at=stored_file.created_at,
                )
            )
        await db.commit()
    except ValueError as err:
        await db.rollback()
        await _cleanup_uploaded_objects(saved_keys)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except StorageError:
        await db.rollback()
        await _cleanup_uploaded_objects(saved_keys)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="File storage is temporarily unavailable")
    except Exception:
        await db.rollback()
        await _cleanup_uploaded_objects(saved_keys)
        raise
    return UploadListResponse(files=uploaded)


@router.get("/admin/list/all", response_model=PaginatedUploadResponse)
async def list_admin_uploads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    file_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
) -> PaginatedUploadResponse:
    """List all stored files for administrative file manager."""
    conditions = []
    if search:
        like = f"%{search}%"
        conditions.append(
            or_(
                StoredFile.original_filename.ilike(like),
                StoredFile.display_filename.ilike(like),
            )
        )
    if file_type and file_type != "all":
        if file_type == "image":
            conditions.append(StoredFile.mime_type.like("image/%"))
        elif file_type == "pdf":
            conditions.append(StoredFile.extension == ".pdf")
        elif file_type == "doc":
            conditions.append(StoredFile.extension.in_([".doc", ".docx"]))

    count_stmt = select(func.count(StoredFile.id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = select(StoredFile).order_by(StoredFile.created_at.desc())
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    files = list(result.scalars().all())

    items = [
        UploadResponse(
            id=f.id,
            original_filename=f.original_filename,
            display_filename=f.display_filename,
            mime_type=f.mime_type,
            extension=f.extension,
            file_size=f.file_size,
            download_url=f"/api/uploads/{f.id}/download",
            created_at=f.created_at,
        )
        for f in files
    ]
    return PaginatedUploadResponse(items=items, total=total, page=page, page_size=page_size)


@router.delete("/admin/{file_id}", response_model=MessageResponse)
async def delete_upload(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> MessageResponse:
    """Delete a stored file after verifying it is not referenced by active notices or documents."""
    result = await db.execute(select(StoredFile).where(StoredFile.id == file_id))
    stored_file = result.scalar_one_or_none()
    if stored_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    # Check references in notices (cover or attachments)
    cov_stmt = select(Notice.id).where(Notice.cover_image_id == file_id)
    if (await db.execute(cov_stmt)).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete file because it is used as a notice cover image",
        )

    att_stmt = select(NoticeAttachment.id).where(NoticeAttachment.file_id == file_id)
    if (await db.execute(att_stmt)).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete file because it is attached to a notice",
        )

    doc_stmt = select(Document.id).where(Document.file_id == file_id)
    if (await db.execute(doc_stmt)).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete file because it is used by a published or draft document",
        )

    gallery_stmt = select(GalleryItem.id).where(GalleryItem.file_id == file_id)
    if (await db.execute(gallery_stmt)).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Remove this image from the gallery before deleting its file",
        )

    storage_key = stored_file.storage_key
    await db.delete(stored_file)
    await db.commit()
    try:
        await _storage_service().delete_file(storage_key)
    except OSError:
        # Metadata is removed; failed physical cleanup leaves an unreachable orphan.
        pass
    except StorageError:
        # The DB metadata is already committed. Leave an unreachable object for later cleanup.
        logger.warning("Storage object cleanup failed after metadata deletion")
    return MessageResponse(message="File deleted successfully")


@router.get("/{file_id}/download")
async def download_file(
    file_id: UUID,
    request: Request,
    preview: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Download or preview a stored file with authorization checks.

    Public visitors may only download files attached to currently published,
    non-expired notices or documents. Authenticated admins have full access.
    """
    # 1. Fetch file record
    result = await db.execute(select(StoredFile).where(StoredFile.id == file_id))
    stored_file = result.scalar_one_or_none()

    if stored_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    # 2. Check if user is authenticated admin/editor
    is_authorized = False
    session_token = request.cookies.get("session_id")
    if session_token:
        token_hash = hash_session_token(session_token)
        s_result = await db.execute(
            select(Session).options(selectinload(Session.user)).where(Session.token_hash == token_hash)
        )
        s_obj = s_result.scalar_one_or_none()
        if s_obj:
            exp_at = s_obj.expires_at
            if exp_at.tzinfo is None:
                exp_at = exp_at.replace(tzinfo=timezone.utc)
            if (
                exp_at > datetime.now(timezone.utc)
                and s_obj.user.is_active
                and s_obj.user.role in {"ADMIN", "EDITOR"}
            ):
                is_authorized = True

    # 3. If not admin, check public eligibility
    if not is_authorized:
        if stored_file.is_public:
            is_authorized = True

    if not is_authorized:
        now = get_db_now(db)

        # Check published notices (as cover or attachment)
        notice_cover_stmt = select(Notice.id).where(
            Notice.cover_image_id == file_id,
            Notice.status == "PUBLISHED",
            Notice.published_at <= now,
            or_(Notice.expires_at.is_(None), Notice.expires_at > now),
        )
        if (await db.execute(notice_cover_stmt)).scalar_one_or_none():
            is_authorized = True

    if not is_authorized:
        now = get_db_now(db)
        notice_att_stmt = (
            select(NoticeAttachment.id)
            .join(Notice, NoticeAttachment.notice_id == Notice.id)
            .where(
                NoticeAttachment.file_id == file_id,
                Notice.status == "PUBLISHED",
                Notice.published_at <= now,
                or_(Notice.expires_at.is_(None), Notice.expires_at > now),
            )
        )
        if (await db.execute(notice_att_stmt)).scalar_one_or_none():
            is_authorized = True

    if not is_authorized:
        now = get_db_now(db)
        doc_stmt = select(Document.id).where(
            Document.file_id == file_id,
            Document.status == "PUBLISHED",
            Document.published_at <= now,
            or_(Document.expires_at.is_(None), Document.expires_at > now),
        )
        if (await db.execute(doc_stmt)).scalar_one_or_none():
            is_authorized = True

    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to download this file",
        )

    # 4. Fetch bytes only after the authorization check above.
    try:
        file_bytes = await get_storage_service_for_file(stored_file).get_file_bytes(stored_file.storage_key)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File binary is missing from storage",
        )
    except StorageError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File storage is temporarily unavailable",
        )

    # 5. Determine inline vs attachment
    is_inline = preview or stored_file.mime_type.startswith("image/") or stored_file.mime_type == "application/pdf"
    disposition = "inline" if is_inline else "attachment"

    from urllib.parse import quote

    encoded_filename = quote(stored_file.display_filename, safe="")
    return Response(
        content=file_bytes,
        media_type=stored_file.mime_type,
        headers={"Content-Disposition": f"{disposition}; filename*=UTF-8''{encoded_filename}"},
    )


async def _cleanup_uploaded_objects(saved: list[tuple[object, str]]) -> None:
    """Best-effort rollback for object uploads if metadata transaction fails."""
    for storage, key in saved:
        try:
            await storage.delete_file(key)
        except (OSError, StorageError, ValueError):
            # The file is unreferenced; cleanup can be retried out of band.
            continue
