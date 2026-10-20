"""Main API router combining all route modules."""

from fastapi import APIRouter

from app.api.routes import admin, auth, documents, gallery, health, inquiries, notices, uploads

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(notices.router)
api_router.include_router(documents.router)
api_router.include_router(uploads.router)
api_router.include_router(gallery.router)
api_router.include_router(inquiries.router)
api_router.include_router(admin.router)

