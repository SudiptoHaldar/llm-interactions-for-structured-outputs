"""CRUD operations for glossary."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.glossary import Glossary


async def get_glossary_entry(db: AsyncSession, glossary_id: int) -> Glossary | None:
    """Get glossary entry by ID."""
    result = await db.execute(
        select(Glossary).where(Glossary.glossary_id == glossary_id)
    )
    return result.scalar_one_or_none()


async def get_glossary_entry_by_name(db: AsyncSession, entry: str) -> Glossary | None:
    """Get glossary entry by entry name (case-insensitive)."""
    result = await db.execute(select(Glossary).where(Glossary.entry.ilike(entry)))
    return result.scalar_one_or_none()


async def get_all_glossary_entries(db: AsyncSession) -> list[Glossary]:
    """Get all glossary entries ordered by entry name."""
    result = await db.execute(select(Glossary).order_by(Glossary.entry))
    return list(result.scalars().all())
