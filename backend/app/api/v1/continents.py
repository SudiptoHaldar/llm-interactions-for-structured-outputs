"""Continents API endpoints."""

from fastapi import APIRouter, HTTPException

from app.crud.continent import get_continent, get_continent_by_name, get_continents
from app.dependencies import DBSession
from app.schemas.continent import ContinentListResponse, ContinentResponse

router = APIRouter(tags=["continents"])


@router.get("/", response_model=ContinentListResponse)
async def list_continents(db: DBSession) -> ContinentListResponse:
    """
    List all continents.

    Returns all continents stored in the database.
    """
    continents = await get_continents(db)
    return ContinentListResponse(
        continents=[ContinentResponse.model_validate(c) for c in continents],
        count=len(continents),
    )


@router.get("/{continent_id}", response_model=ContinentResponse)
async def get_continent_by_id(continent_id: int, db: DBSession) -> ContinentResponse:
    """
    Get continent by ID.

    Returns a single continent by its unique identifier.
    """
    continent = await get_continent(db, continent_id)
    if continent is None:
        raise HTTPException(status_code=404, detail="Continent not found")
    return ContinentResponse.model_validate(continent)


@router.get("/name/{continent_name}", response_model=ContinentResponse)
async def get_continent_by_name_endpoint(
    continent_name: str, db: DBSession
) -> ContinentResponse:
    """
    Get continent by name.

    Returns a single continent by its name (case-insensitive).
    """
    continent = await get_continent_by_name(db, continent_name)
    if continent is None:
        raise HTTPException(status_code=404, detail="Continent not found")
    return ContinentResponse.model_validate(continent)
