"""Cities API endpoints."""

from fastapi import APIRouter, HTTPException

from app.crud.city import (
    get_cities,
    get_cities_by_country_id,
    get_cities_by_country_name,
    get_city,
    get_city_by_name,
)
from app.dependencies import DBSession
from app.schemas.city import CityListResponse, CityResponse

router = APIRouter(tags=["cities"])


@router.get("/", response_model=CityListResponse)
async def list_cities(db: DBSession) -> CityListResponse:
    """
    List all cities.

    Returns all cities stored in the database.
    """
    cities = await get_cities(db)
    return CityListResponse(
        cities=[CityResponse.model_validate(c) for c in cities],
        count=len(cities),
    )


@router.get("/name/{city_name}", response_model=CityResponse)
async def get_city_by_name_endpoint(city_name: str, db: DBSession) -> CityResponse:
    """
    Get city by name.

    Returns a single city by its name (case-insensitive).
    """
    city = await get_city_by_name(db, city_name)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return CityResponse.model_validate(city)


@router.get("/country/name/{country_name}", response_model=CityListResponse)
async def get_cities_by_country_name_endpoint(
    country_name: str, db: DBSession
) -> CityListResponse:
    """
    Get cities by country name.

    Returns all cities belonging to the specified country (case-insensitive).
    """
    cities = await get_cities_by_country_name(db, country_name)
    return CityListResponse(
        cities=[CityResponse.model_validate(c) for c in cities],
        count=len(cities),
    )


@router.get("/country/{country_id}", response_model=CityListResponse)
async def get_cities_by_country_id_endpoint(
    country_id: int, db: DBSession
) -> CityListResponse:
    """
    Get cities by country ID.

    Returns all cities belonging to the specified country.
    """
    cities = await get_cities_by_country_id(db, country_id)
    return CityListResponse(
        cities=[CityResponse.model_validate(c) for c in cities],
        count=len(cities),
    )


@router.get("/{city_id}", response_model=CityResponse)
async def get_city_by_id(city_id: int, db: DBSession) -> CityResponse:
    """
    Get city by ID.

    Returns a single city by its unique identifier.
    """
    city = await get_city(db, city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return CityResponse.model_validate(city)
