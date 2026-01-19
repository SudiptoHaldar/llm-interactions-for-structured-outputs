"""Countries API endpoints."""

from fastapi import APIRouter, HTTPException

from app.crud.country import (
    get_countries,
    get_countries_by_continent_id,
    get_countries_by_continent_name,
    get_countries_by_model_id,
    get_countries_by_model_name,
    get_country,
    get_country_by_name,
)
from app.dependencies import DBSession
from app.schemas.country import CountryListResponse, CountryResponse

router = APIRouter(tags=["countries"])


@router.get("/", response_model=CountryListResponse)
async def list_countries(db: DBSession) -> CountryListResponse:
    """
    List all countries.

    Returns all countries stored in the database.
    """
    countries = await get_countries(db)
    return CountryListResponse(
        countries=[CountryResponse.model_validate(c) for c in countries],
        count=len(countries),
    )


@router.get("/{country_id}", response_model=CountryResponse)
async def get_country_by_id(country_id: int, db: DBSession) -> CountryResponse:
    """
    Get country by ID.

    Returns a single country by its unique identifier.
    """
    country = await get_country(db, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return CountryResponse.model_validate(country)


@router.get("/name/{country_name}", response_model=CountryResponse)
async def get_country_by_name_endpoint(
    country_name: str, db: DBSession
) -> CountryResponse:
    """
    Get country by name.

    Returns a single country by its name (case-insensitive).
    """
    country = await get_country_by_name(db, country_name)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return CountryResponse.model_validate(country)


@router.get("/continent/{continent_id}", response_model=CountryListResponse)
async def get_countries_by_continent_id_endpoint(
    continent_id: int, db: DBSession
) -> CountryListResponse:
    """
    Get countries by continent ID.

    Returns all countries belonging to the specified continent.
    """
    countries = await get_countries_by_continent_id(db, continent_id)
    return CountryListResponse(
        countries=[CountryResponse.model_validate(c) for c in countries],
        count=len(countries),
    )


@router.get("/continent/name/{continent_name}", response_model=CountryListResponse)
async def get_countries_by_continent_name_endpoint(
    continent_name: str, db: DBSession
) -> CountryListResponse:
    """
    Get countries by continent name.

    Returns all countries belonging to the specified continent (case-insensitive).
    """
    countries = await get_countries_by_continent_name(db, continent_name)
    return CountryListResponse(
        countries=[CountryResponse.model_validate(c) for c in countries],
        count=len(countries),
    )


@router.get("/model/name/{model_name}", response_model=CountryListResponse)
async def get_countries_by_model_name_endpoint(
    model_name: str, db: DBSession
) -> CountryListResponse:
    """
    Get countries by AI model provider name.

    Returns all countries whose data was provided by the specified AI model provider.
    Examples: Google, DeepSeek, OpenAI, Anthropic, Cohere, Groq, Mistral, AI21.
    """
    countries = await get_countries_by_model_name(db, model_name)
    return CountryListResponse(
        countries=[CountryResponse.model_validate(c) for c in countries],
        count=len(countries),
    )


@router.get("/model/{model_id}", response_model=CountryListResponse)
async def get_countries_by_model_id_endpoint(
    model_id: int, db: DBSession
) -> CountryListResponse:
    """
    Get countries by AI model ID.

    Returns all countries whose data was provided by the specified AI model.
    """
    countries = await get_countries_by_model_id(db, model_id)
    return CountryListResponse(
        countries=[CountryResponse.model_validate(c) for c in countries],
        count=len(countries),
    )
