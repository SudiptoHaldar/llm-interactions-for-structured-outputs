"""City Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CityResponse(BaseModel):
    """City response schema."""

    model_config = ConfigDict(from_attributes=True)

    city_id: int
    country_id: int | None
    name: str
    is_capital: bool | None
    description: str | None
    interesting_fact: str | None
    area_sq_mile: float | None
    area_sq_km: float | None
    population: int | None
    sci_score: float | None
    sci_rank: int | None
    numbeo_si: float | None
    numbeo_ci: float | None
    airport_code: str | None
    created_at: datetime
    updated_at: datetime


class CityListResponse(BaseModel):
    """City list response schema."""

    cities: list[CityResponse]
    count: int
