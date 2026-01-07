"""CRUD operations for countries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_model import AIModel
from app.models.continent import Continent
from app.models.country import Country


async def get_country(db: AsyncSession, country_id: int) -> Country | None:
    """Get country by ID."""
    result = await db.execute(
        select(Country).where(Country.country_id == country_id)
    )
    return result.scalar_one_or_none()


async def get_country_by_name(db: AsyncSession, name: str) -> Country | None:
    """Get country by name (case-insensitive)."""
    result = await db.execute(select(Country).where(Country.name.ilike(name)))
    return result.scalar_one_or_none()


async def get_countries(db: AsyncSession) -> list[Country]:
    """Get all countries."""
    result = await db.execute(select(Country).order_by(Country.name))
    return list(result.scalars().all())


async def get_countries_by_continent_id(
    db: AsyncSession, continent_id: int
) -> list[Country]:
    """Get countries by continent ID."""
    result = await db.execute(
        select(Country)
        .where(Country.continent_id == continent_id)
        .order_by(Country.name)
    )
    return list(result.scalars().all())


async def get_countries_by_continent_name(
    db: AsyncSession, continent_name: str
) -> list[Country]:
    """Get countries by continent name (case-insensitive)."""
    result = await db.execute(
        select(Country)
        .join(Continent, Country.continent_id == Continent.continent_id)
        .where(Continent.continent_name.ilike(continent_name))
        .order_by(Country.name)
    )
    return list(result.scalars().all())


async def get_countries_by_model_id(
    db: AsyncSession, model_id: int
) -> list[Country]:
    """Get countries by AI model ID."""
    result = await db.execute(
        select(Country).where(Country.ai_model_id == model_id).order_by(Country.name)
    )
    return list(result.scalars().all())


async def get_countries_by_model_name(
    db: AsyncSession, model_name: str
) -> list[Country]:
    """Get countries by AI model provider name (case-insensitive)."""
    result = await db.execute(
        select(Country)
        .join(AIModel, Country.ai_model_id == AIModel.ai_model_id)
        .where(AIModel.model_provider.ilike(model_name))
        .order_by(Country.name)
    )
    return list(result.scalars().all())
