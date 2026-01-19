"""OpenAI provider for structured outputs."""

import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from process_structured_output.models.continent import ContinentInfo, ModelIdentity
from process_structured_output.models.country import (
    CitiesResponse,
    CityInfo,
    CountryInfo,
)
from process_structured_output.prompts import (
    CITY_SYSTEM_PROMPT,
    COUNTRY_SYSTEM_PROMPT,
    get_cities_user_prompt,
    get_country_user_prompt,
    truncate_city_strings,
    truncate_country_strings,
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


class OpenAIProvider:
    """OpenAI API provider for structured continent information."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key. If not provided, reads from env var.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"

    def get_model_identity(self) -> ModelIdentity:
        """
        Return hardcoded model identity for OpenAI.

        Note: LLMs cannot reliably self-identify as they may have been trained
        on data from other models. Using hardcoded values ensures consistency.

        Returns:
            ModelIdentity with model_provider="OpenAI" and model_name

        Example:
            >>> provider = OpenAIProvider()
            >>> identity = provider.get_model_identity()
            >>> print(identity.model_provider)
            OpenAI
        """
        return ModelIdentity(
            model_provider="OpenAI",
            model_name=self.model,
        )

    def get_continent_info(self, continent_name: str) -> ContinentInfo:
        """
        Get structured continent information from OpenAI.

        Args:
            continent_name: Name of the continent to query

        Returns:
            ContinentInfo with structured data

        Example:
            >>> provider = OpenAIProvider()
            >>> info = provider.get_continent_info("Africa")
            >>> print(info.population)
            1400000000
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI geography teacher knowledgeable on "
                        "world geography, continents and countries. Respond with "
                        "accurate geographic data in the exact JSON format requested. "
                        "When asked about a continent, provide data for the entire "
                        "continental region including all sovereign nations within it."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Please provide the information on the continent of "
                        f"{continent_name} in JSON format with these fields:\n"
                        "- description: less than 250 characters\n"
                        "- area_sq_mile: total area in square miles (number)\n"
                        "- area_sq_km: total area in square km (number)\n"
                        "- population: total population of all countries (integer)\n"
                        "- num_country: total number of sovereign nations in the "
                        "continental region (integer)"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
        )

        content = response.choices[0].message.content or "{}"

        try:
            data = json.loads(content)
            return ContinentInfo(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Failed to parse continent info: {e}") from e

    def get_country_info(self, country_name: str) -> CountryInfo:
        """Get structured country information from OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": COUNTRY_SYSTEM_PROMPT},
                {"role": "user", "content": get_country_user_prompt(country_name)},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            if not data:
                raise ValueError("Empty JSON response from OpenAI")
            # Truncate strings to enforce character limits
            data = truncate_country_strings(data)
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
        """Get structured city information from OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": CITY_SYSTEM_PROMPT},
                {"role": "user", "content": get_cities_user_prompt(country_name)},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            # Sanitize and truncate each city before validation
            if "cities" in data:
                data["cities"] = [
                    truncate_city_strings(_sanitize_city_data(c))
                    for c in data["cities"]
                ]
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
