"""Database session management."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Get cached database engine instance."""
    settings = get_settings()
    # Ensure URL uses asyncpg driver
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://", 1
        )
    return create_async_engine(
        database_url,
        echo=settings.debug_mode,
        pool_pre_ping=True,
    )


@lru_cache
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get cached session maker instance."""
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with get_session_maker()() as session:
        try:
            yield session
        finally:
            await session.close()
