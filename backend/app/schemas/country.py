"""Country Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CountryResponse(BaseModel):
    """Country response schema."""

    model_config = ConfigDict(from_attributes=True)

    country_id: int
    name: str
    description: str | None
    interesting_fact: str | None
    area_sq_mile: float | None
    area_sq_km: float | None
    population: int | None
    ppp: float | None
    life_expectancy: float | None
    travel_risk_level: str | None
    global_peace_index_score: float | None
    global_peace_index_rank: int | None
    happiness_index_score: float | None
    happiness_index_rank: int | None
    gdp: float | None
    gdp_growth_rate: float | None
    inflation_rate: float | None
    unemployment_rate: float | None
    govt_debt: float | None
    credit_rating: str | None
    poverty_rate: float | None
    gini_coefficient: float | None
    military_spending: float | None
    continent_id: int | None
    ai_model_id: int | None
    created_at: datetime
    updated_at: datetime


class CountryListResponse(BaseModel):
    """Country list response schema."""

    countries: list[CountryResponse]
    count: int
