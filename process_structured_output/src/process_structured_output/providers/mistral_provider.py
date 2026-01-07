"""Mistral LLM provider for structured outputs.

Uses Mistral's Python SDK with JSON mode for structured output generation.
"""

import json
import os
import time

from dotenv import load_dotenv
from mistralai import Mistral
from pydantic import ValidationError

from process_structured_output.models.continent import ContinentInfo, ModelIdentity
from process_structured_output.models.country import (
    CitiesResponse,
    CityInfo,
    CountryInfo,
)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0


def _sanitize_city_data(city: dict) -> dict:
    """Sanitize city data from LLM responses.

    Handles common issues:
    - Converts empty/invalid airport_code to None (some cities lack airports)

    Args:
        city: Dictionary of city field values

    Returns:
        Dictionary with sanitized values
    """
    if "airport_code" in city:
        code = city["airport_code"]
        if code is None or (isinstance(code, str) and len(code) < 3):
            city["airport_code"] = None
    return city


class MistralProvider:
    """Mistral LLM provider using Mistral's Python SDK."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "mistral-large-latest",
    ) -> None:
        """Initialize the Mistral provider.

        Args:
            api_key: Mistral API key. If not provided, reads from
                MISTRAL_API_KEY env var.
            model: Model name to use.
        """
        load_dotenv()

        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY environment variable not set. "
                "Please set it in your .env file or pass api_key parameter."
            )

        self.model = model
        self.client = Mistral(api_key=self.api_key)

    def get_model_identity(self) -> ModelIdentity:
        """Return hardcoded model identity for Mistral.

        Note: LLMs cannot reliably self-identify as they may have been
        trained on data from other models. Using hardcoded values ensures
        consistency.
        """
        return ModelIdentity(
            model_provider="Mistral",
            model_name=self.model,
        )

    def get_continent_info(self, continent_name: str) -> ContinentInfo:
        """Get structured continent information from Mistral."""
        response = self.client.chat.complete(
            model=self.model,
            messages=[  # type: ignore[arg-type]
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI geography teacher. "
                        "Always respond with valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Provide information about the continent {continent_name} "
                        "as a JSON object with these exact fields:\n"
                        "- description: string (less than 250 characters)\n"
                        "- area_sq_mile: number (area in square miles)\n"
                        "- area_sq_km: number (area in square km)\n"
                        "- population: integer\n"
                        "- num_country: integer (number of countries)"
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )

        content = str(response.choices[0].message.content) or "{}"
        try:
            data = json.loads(content)
            return ContinentInfo(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Failed to parse continent info: {e}") from e

    def get_country_info(self, country_name: str) -> CountryInfo:
        """Get structured country information from Mistral."""
        response = self.client.chat.complete(
            model=self.model,
            messages=[  # type: ignore[arg-type]
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI geography teacher knowledgeable on "
                        "world geography, continents and countries. "
                        "Always respond with valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Provide information about the country {country_name} "
                        "as a JSON object with these exact fields:\n"
                        "- description: string (less than 250 characters)\n"
                        "- interesting_fact: string (less than 250 characters)\n"
                        "- area_sq_mile: number (area in square miles)\n"
                        "- area_sq_km: number (area in square km)\n"
                        "- population: integer\n"
                        "- ppp: number (purchasing power parity in $)\n"
                        "- life_expectancy: number (in years)\n"
                        "- travel_risk_level: string (US advisory level)\n"
                        "- global_peace_index_score: number (IEP score)\n"
                        "- global_peace_index_rank: integer (IEP rank)\n"
                        "- happiness_index_score: number (Oxford score)\n"
                        "- happiness_index_rank: integer (Oxford rank)\n"
                        "- gdp: number (in $)\n"
                        "- gdp_growth_rate: number (in %)\n"
                        "- inflation_rate: number (in %)\n"
                        "- unemployment_rate: number (in %)\n"
                        "- govt_debt: number (in % of GDP)\n"
                        "- credit_rating: string (S&P rating)\n"
                        "- poverty_rate: number (in %)\n"
                        "- gini_coefficient: number (income inequality)\n"
                        "- military_spending: number (in % of GDP)"
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )

        content = str(response.choices[0].message.content) or "{}"
        try:
            data = json.loads(content)
            if not data:
                raise ValueError("Empty JSON response from Mistral")
            return CountryInfo(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse country info: {e}") from e
        except ValidationError as e:
            raise ValueError(f"Failed to parse country info: {e}") from e

    def get_country_info_with_retry(
        self, country_name: str, max_retries: int = MAX_RETRIES
    ) -> CountryInfo:
        """Get country info with retry logic."""
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                return self.get_country_info(country_name)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY)
        raise ValueError(
            f"Failed after {max_retries} retries: {last_error}"
        ) from last_error

    def get_cities_info(self, country_name: str) -> list[CityInfo]:
        """Get structured city information from Mistral."""
        response = self.client.chat.complete(
            model=self.model,
            messages=[  # type: ignore[arg-type]
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI geography teacher knowledgeable on "
                        "world geography, continents, countries, and cities. "
                        "Always respond with valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"List up to 5 most populous cities in {country_name}. "
                        "Return a JSON object with a 'cities' array. "
                        "Each city should have these fields:\n"
                        "- name: string\n"
                        "- is_capital: boolean\n"
                        "- description: string (less than 250 characters)\n"
                        "- interesting_fact: string (less than 250 characters)\n"
                        "- area_sq_mile: number\n"
                        "- area_sq_km: number\n"
                        "- population: integer\n"
                        "- sci_score: number or null (EIU Safe Cities Index)\n"
                        "- sci_rank: integer or null (EIU Safe Cities Index rank)\n"
                        "- numbeo_si: number or null (Numbeo Safety Index 0-100)\n"
                        "- numbeo_ci: number or null (Numbeo Crime Index 0-100)\n"
                        "- airport_code: string (3-letter IATA code)"
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )

        content = str(response.choices[0].message.content) or "{}"
        try:
            data = json.loads(content)
            # Sanitize city data before validation
            if "cities" in data:
                data["cities"] = [_sanitize_city_data(c) for c in data["cities"]]
            cities_response = CitiesResponse(**data)
            return cities_response.cities
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Failed to parse cities info: {e}") from e

    def get_cities_info_with_retry(
        self, country_name: str, max_retries: int = MAX_RETRIES
    ) -> list[CityInfo]:
        """Get cities info with retry logic."""
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                return self.get_cities_info(country_name)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY)
        raise ValueError(
            f"Failed after {max_retries} retries: {last_error}"
        ) from last_error
