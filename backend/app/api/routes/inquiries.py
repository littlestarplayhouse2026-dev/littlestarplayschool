"""Contact inquiries routes."""

from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_admin, verify_csrf
from app.models.inquiry import Inquiry
from app.models.inquiry_rate_limit import InquiryRateLimit
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.inquiry import InquiryCreate, InquiryListResponse, InquiryResponse
from app.utils.datetime_utils import get_db_now

router = APIRouter(prefix="/inquiries", tags=["Inquiries"])


class InquiryStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(NEW|REVIEWED|CONTACTED|CLOSED)$")


@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_inquiry(
    request: Request,
    data: InquiryCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Public contact/admission inquiry form submission."""
    # A quietly discarded honeypot submission blocks common automated spam.
    if data.website.strip():
        return {"message": "Thank you for reaching out! Little Star Playhouse has received your enquiry.", "id": ""}
    client_ip = request.client.host if request.client else "0.0.0.0"
    window_start = get_db_now(db) - timedelta(minutes=10)
    count = await db.execute(select(func.count(InquiryRateLimit.id)).where(
        InquiryRateLimit.ip_address == client_ip,
        InquiryRateLimit.created_at >= window_start,
    ))
    if count.scalar_one() >= 5:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many enquiries. Please try again later.")
    await db.execute(delete(InquiryRateLimit).where(InquiryRateLimit.created_at < window_start))
    db.add(InquiryRateLimit(ip_address=client_ip))

    inquiry = Inquiry(
        parent_name=data.parent_name,
        phone=data.phone,
        email=data.email,
        child_age=data.child_age,
        program=data.program,
        message=data.message,
        status="NEW",
    )
    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)

    return {
        "message": "Thank you for reaching out! Little Star Playhouse has received your enquiry.",
        "id": str(inquiry.id),
    }


@router.get("/admin/list/all", response_model=InquiryListResponse)
async def list_admin_inquiries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
) -> InquiryListResponse:
    """Protected list of contact and admission inquiries with search and status filtering."""
    conditions = []
    if search:
        like = f"%{search}%"
        conditions.append(
            or_(
                Inquiry.parent_name.ilike(like),
                Inquiry.phone.ilike(like),
                Inquiry.email.ilike(like),
            )
        )
    if status_filter and status_filter.upper() != "ALL":
        conditions.append(Inquiry.status == status_filter.upper())

    count_stmt = select(func.count(Inquiry.id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = select(Inquiry).order_by(Inquiry.created_at.desc())
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    inquiries = list(result.scalars().all())

    items = [InquiryResponse.model_validate(item) for item in inquiries]
    return InquiryListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/admin/{inquiry_id}", response_model=InquiryResponse)
async def get_admin_inquiry(
    inquiry_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
) -> InquiryResponse:
    """Retrieve full detail of an inquiry."""
    result = await db.execute(select(Inquiry).where(Inquiry.id == inquiry_id))
    inquiry = result.scalar_one_or_none()
    if inquiry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )
    return InquiryResponse.model_validate(inquiry)


@router.patch("/admin/{inquiry_id}", response_model=InquiryResponse)
async def update_inquiry_status(
    inquiry_id: UUID,
    payload: InquiryStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
    _csrf: None = Depends(verify_csrf),
) -> InquiryResponse:
    """Update processing status of an inquiry."""
    result = await db.execute(select(Inquiry).where(Inquiry.id == inquiry_id))
    inquiry = result.scalar_one_or_none()
    if inquiry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )
    inquiry.status = payload.status
    await db.commit()
    await db.refresh(inquiry)
    return InquiryResponse.model_validate(inquiry)


@router.delete("/admin/{inquiry_id}", response_model=MessageResponse)
async def delete_inquiry(
    inquiry_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_admin),
    _csrf: None = Depends(verify_csrf),
) -> MessageResponse:
    """Delete an inquiry."""
    result = await db.execute(select(Inquiry).where(Inquiry.id == inquiry_id))
    inquiry = result.scalar_one_or_none()
    if inquiry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found",
        )
    await db.delete(inquiry)
    await db.commit()
    return MessageResponse(message="Inquiry deleted successfully")
