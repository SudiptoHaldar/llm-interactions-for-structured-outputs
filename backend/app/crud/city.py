"""CRUD operations for cities."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.city import City
from app.models.country import Country


async def get_city(db: AsyncSession, city_id: int) -> City | None:
    """Get city by ID."""
    result = await db.execute(select(City).where(City.city_id == city_id))
    return result.scalar_one_or_none()


async def get_city_by_name(db: AsyncSession, name: str) -> City | None:
    """Get city by name (case-insensitive)."""
    result = await db.execute(select(City).where(City.name.ilike(name)))
    return result.scalar_one_or_none()


async def get_cities(db: AsyncSession) -> list[City]:
    """Get all cities."""
    result = await db.execute(select(City).order_by(City.name))
    return list(result.scalars().all())


async def get_cities_by_country_id(db: AsyncSession, country_id: int) -> list[City]:
    """Get cities by country ID."""
    result = await db.execute(
        select(City).where(City.country_id == country_id).order_by(City.name)
    )
    return list(result.scalars().all())


async def get_cities_by_country_name(db: AsyncSession, country_name: str) -> list[City]:
    """Get cities by country name (case-insensitive)."""
    result = await db.execute(
        select(City)
        .join(Country, City.country_id == Country.country_id)
        .where(Country.name.ilike(country_name))
        .order_by(City.name)
    )
    return list(result.scalars().all())
