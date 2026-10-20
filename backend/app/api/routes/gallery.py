"""Public gallery listing and admin image management."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.dependencies import get_db, require_editor_or_admin, verify_csrf
from app.models.gallery_item import GalleryItem
from app.models.stored_file import StoredFile
from app.models.user import User
from app.schemas.gallery import GalleryItemResponse, GalleryListResponse
from app.schemas.auth import MessageResponse
from app.services.storage_service import LocalStorageService

router = APIRouter(prefix="/gallery", tags=["Gallery"])
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _storage_service() -> LocalStorageService:
    return LocalStorageService(upload_dir=settings.UPLOAD_DIR, max_file_bytes=settings.max_upload_bytes)


@router.get("", response_model=GalleryListResponse)
async def list_gallery(db: AsyncSession = Depends(get_db)) -> GalleryListResponse:
    result = await db.execute(
        select(GalleryItem).options(selectinload(GalleryItem.file)).order_by(GalleryItem.created_at.desc())
    )
    return GalleryListResponse(items=[
        GalleryItemResponse(
            id=item.id,
            file_id=item.file_id,
            caption=item.caption,
            image_url=f"/api/uploads/{item.file_id}/download",
            created_at=item.created_at,
        )
        for item in result.scalars().all()
    ])


@router.post("/admin/images", response_model=GalleryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_gallery_image(
    image: UploadFile = File(...),
    caption: str = Form(..., min_length=1, max_length=500),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> GalleryItemResponse:
    extension = Path(image.filename or "").suffix.lower()
    supplied_mime = (image.content_type or "").split(";", 1)[0].strip().lower()
    if extension not in IMAGE_EXTENSIONS or (
        supplied_mime and not supplied_mime.startswith("image/") and supplied_mime != "application/octet-stream"
    ):
        raise HTTPException(status_code=400, detail="Choose a JPG, PNG, or WebP image")
    if image.size and image.size > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"Image exceeds {settings.MAX_UPLOAD_MB} MB")
    caption = caption.strip()
    if not caption:
        raise HTTPException(status_code=400, detail="Caption is required")

    stored_file = None
    storage = _storage_service()
    try:
        stored_file = await storage.save_file(file=image, uploader_id=user.id, is_public=True)
        db.add(stored_file)
        await db.flush()
        item = GalleryItem(file_id=stored_file.id, caption=caption)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return GalleryItemResponse(
            id=item.id, file_id=item.file_id, caption=item.caption,
            image_url=f"/api/uploads/{item.file_id}/download", created_at=item.created_at,
        )
    except ValueError as err:
        await db.rollback()
        if stored_file:
            await storage.delete_file(stored_file.storage_key)
        raise HTTPException(status_code=400, detail=str(err))
    except Exception:
        await db.rollback()
        if stored_file:
            await storage.delete_file(stored_file.storage_key)
        raise


@router.delete("/admin/{item_id}", response_model=MessageResponse)
async def delete_gallery_image(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> MessageResponse:
    item = await db.get(GalleryItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Gallery image not found")
    stored_file = await db.get(StoredFile, item.file_id)
    if stored_file:
        stored_file.is_public = False
    await db.delete(item)
    await db.commit()
    return MessageResponse(message="Gallery image removed")
