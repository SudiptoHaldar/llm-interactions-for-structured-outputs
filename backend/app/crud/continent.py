"""CRUD operations for continents."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.continent import Continent


async def get_continent(db: AsyncSession, continent_id: int) -> Continent | None:
    """Get continent by ID."""
    result = await db.execute(
        select(Continent).where(Continent.continent_id == continent_id)
    )
    return result.scalar_one_or_none()


async def get_continent_by_name(db: AsyncSession, name: str) -> Continent | None:
    """Get continent by name (case-insensitive)."""
    result = await db.execute(
        select(Continent).where(Continent.continent_name.ilike(name))
    )
    return result.scalar_one_or_none()


async def get_continents(db: AsyncSession) -> list[Continent]:
    """Get all continents."""
    result = await db.execute(select(Continent).order_by(Continent.continent_id))
    return list(result.scalars().all())
