"""Continent Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContinentResponse(BaseModel):
    """Continent response schema."""

    model_config = ConfigDict(from_attributes=True)

    continent_id: int
    continent_name: str
    description: str | None
    area_sq_mile: float | None
    area_sq_km: float | None
    population: int | None
    num_country: int | None
    ai_model_id: int | None
    created_at: datetime
    updated_at: datetime


class ContinentListResponse(BaseModel):
    """Continent list response schema."""

    continents: list[ContinentResponse]
    count: int
