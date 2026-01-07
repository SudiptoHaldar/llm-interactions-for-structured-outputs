"""Pydantic models for country and city structured output."""

from pydantic import BaseModel, ConfigDict, Field


class CountryInfo(BaseModel):
    """Country information response from LLM."""

    model_config = ConfigDict(strict=True)

    description: str = Field(
        ...,
        description="Brief description of the country",
        max_length=250,
    )
    interesting_fact: str = Field(
        ...,
        description="Notable fact about the country",
        max_length=250,
    )
    area_sq_mile: float = Field(
        ...,
        description="Total area in square miles",
        gt=0,
    )
    area_sq_km: float = Field(
        ...,
        description="Total area in square kilometers",
        gt=0,
    )
    population: int = Field(
        ...,
        description="Total population",
        gt=0,
    )
    ppp: float = Field(
        ...,
        description="Purchasing power parity in USD",
        ge=0,
    )
    life_expectancy: float = Field(
        ...,
        description="Life expectancy in years",
        gt=0,
        le=150,
    )
    travel_risk_level: str = Field(
        ...,
        description=(
            "US State Dept advisory in format 'Level X: Description' "
            "where X is 1-4 (e.g., 'Level 3: Reconsider Travel')"
        ),
        max_length=50,
    )
    global_peace_index_score: float = Field(
        ...,
        description="Global Peace Index score (IEP)",
        ge=0,
    )
    global_peace_index_rank: int = Field(
        ...,
        description="Global Peace Index rank",
        ge=1,
    )
    happiness_index_score: float = Field(
        ...,
        description="World Happiness Report score",
        ge=0,
    )
    happiness_index_rank: int = Field(
        ...,
        description="World Happiness Report rank",
        ge=1,
    )
    gdp: float = Field(
        ...,
        description="GDP in USD",
        ge=0,
    )
    gdp_growth_rate: float = Field(
        ...,
        description="GDP growth rate percentage",
    )
    inflation_rate: float = Field(
        ...,
        description="Inflation rate percentage",
    )
    unemployment_rate: float = Field(
        ...,
        description="Unemployment rate percentage",
        ge=0,
    )
    govt_debt: float = Field(
        ...,
        description="Government debt as percentage of GDP",
        ge=0,
    )
    credit_rating: str = Field(
        ...,
        description="S&P credit rating",
        max_length=10,
    )
    poverty_rate: float = Field(
        ...,
        description="Poverty rate percentage",
        ge=0,
    )
    gini_coefficient: float = Field(
        ...,
        description="Gini coefficient (income inequality)",
        ge=0,
        le=100,
    )
    military_spending: float = Field(
        ...,
        description="Military spending as percentage of GDP",
        ge=0,
    )


class CityInfo(BaseModel):
    """City information response from LLM."""

    model_config = ConfigDict(strict=True)

    name: str = Field(
        ...,
        description="City name",
        max_length=100,
    )
    is_capital: bool = Field(
        ...,
        description="Whether this city is the capital",
    )
    description: str = Field(
        ...,
        description="Brief description of the city",
        max_length=250,
    )
    interesting_fact: str = Field(
        ...,
        description="Notable fact about the city",
        max_length=250,
    )
    area_sq_mile: float = Field(
        ...,
        description="Total area in square miles",
        gt=0,
    )
    area_sq_km: float = Field(
        ...,
        description="Total area in square kilometers",
        gt=0,
    )
    population: int = Field(
        ...,
        description="Total population",
        gt=0,
    )
    sci_score: float | None = Field(
        None,
        description="EIU Safe Cities Index score (0-100)",
        ge=0,
        le=100,
    )
    sci_rank: int | None = Field(
        None,
        description="EIU Safe Cities Index rank",
        ge=1,
    )
    numbeo_si: float | None = Field(
        None,
        description="Numbeo Safety Index (0-100)",
        ge=0,
        le=100,
    )
    numbeo_ci: float | None = Field(
        None,
        description="Numbeo Crime Index (0-100)",
        ge=0,
        le=100,
    )
    airport_code: str | None = Field(
        None,
        description="IATA 3-letter airport code (None if no nearby airport)",
        min_length=3,
        max_length=3,
    )


class CitiesResponse(BaseModel):
    """Response containing list of cities from LLM."""

    cities: list[CityInfo] = Field(
        ...,
        description="List of cities",
        max_length=5,
    )
