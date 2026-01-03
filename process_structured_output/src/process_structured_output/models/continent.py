"""Pydantic models for continent structured output."""

from pydantic import BaseModel, ConfigDict, Field


class ModelIdentity(BaseModel):
    """Model identity response from LLM."""

    model_config = ConfigDict(strict=True)

    model_provider: str = Field(
        ...,
        description="AI provider name (e.g., OpenAI, Anthropic)",
        max_length=50,
    )
    model_name: str = Field(
        ...,
        description="Model identifier (e.g., gpt-4o, claude-3-opus)",
        max_length=100,
    )


class ContinentInfo(BaseModel):
    """Continent information response from LLM."""

    model_config = ConfigDict(strict=True)

    description: str = Field(
        ...,
        description="Brief description of the continent",
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
    num_country: int = Field(
        ...,
        description="Number of countries from geopolitical perspective",
        ge=0,
    )
