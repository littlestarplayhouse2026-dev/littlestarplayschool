"""Document routes for public visitors and authenticated administrators."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_editor_or_admin, verify_csrf
from app.models.document import Document
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.document import (
    DocumentCreate,
    DocumentFileInfo,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])


def _build_document_response(doc: Document) -> DocumentResponse:
    """Helper to convert a Document model with relationships into DocumentResponse."""
    file_info = DocumentFileInfo(
        id=doc.file.id if doc.file else doc.file_id,
        original_filename=doc.file.original_filename if doc.file else "document",
        mime_type=doc.file.mime_type if doc.file else "application/octet-stream",
        extension=doc.file.extension if doc.file else "",
        file_size=doc.file.file_size if doc.file else 0,
    )
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        description=doc.description,
        category=doc.category,
        status=doc.status,
        file=file_info,
        download_url=f"/api/uploads/{doc.file_id}/download",
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        published_at=doc.published_at,
        expires_at=doc.expires_at,
    )


# ─── Public Endpoints ─────────────────────────────────────────────

@router.get("", response_model=DocumentListResponse)
async def list_public_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    search: str | None = None,
    category: str | None = None,
    file_type: str | None = None,
    sort: str = "newest",
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """Public list of published, active parent resources and documents."""
    docs, total = await document_service.get_public_documents(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        file_type=file_type,
        sort=sort,
    )
    items = [_build_document_response(d) for d in docs]
    return DocumentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/admin/list/all", response_model=DocumentListResponse)
async def list_admin_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
) -> DocumentListResponse:
    """Protected list of all documents for administrators."""
    docs, total = await document_service.get_admin_documents(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        status=status,
    )
    items = [_build_document_response(d) for d in docs]
    return DocumentListResponse(items=items, total=total, page=page, page_size=page_size)


# ─── Admin Endpoints ──────────────────────────────────────────────

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> DocumentResponse:
    """Create a new document record."""
    try:
        doc = await document_service.create_document(db, data, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A concurrent change conflicted with this document. Refresh and try again.",
        ) from exc
    return _build_document_response(doc)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> DocumentResponse:
    """Update an existing document."""
    try:
        doc = await document_service.update_document(db, document_id, data)
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if str(exc) == "Document not found" else 422
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A concurrent change conflicted with this document. Refresh and try again.",
        ) from exc
    return _build_document_response(doc)


@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_editor_or_admin),
    _csrf: None = Depends(verify_csrf),
) -> MessageResponse:
    """Delete a document."""
    await document_service.delete_document(db, document_id)
    return MessageResponse(message="Document deleted successfully")

