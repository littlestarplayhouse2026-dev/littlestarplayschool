"""Database engine and async session factory."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger(__name__)

engine_kwargs: dict = {
    "echo": settings.ENVIRONMENT == "development",
}

database_url = settings.sqlalchemy_database_url

if not database_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    })

engine = create_async_engine(database_url, **engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncSession:  # type: ignore[misc]
    """Async generator that yields a database session and ensures cleanup."""
    async with async_session_factory() as session:
        yield session
