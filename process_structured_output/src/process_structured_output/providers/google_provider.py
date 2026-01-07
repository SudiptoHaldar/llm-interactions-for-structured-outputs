"""Google Gemini provider for structured outputs."""

import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from process_structured_output.models.continent import ContinentInfo, ModelIdentity
from process_structured_output.models.country import (
    CityInfo,
    CountryInfo,
)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds


def _sanitize_city_data(data: dict, max_length: int = 250) -> dict:
    """
    Sanitize city data from Gemini responses.

    Handles common issues:
    - Truncates description/interesting_fact fields that exceed max_length
    - Converts empty airport_code strings to None

    Args:
        data: Dictionary of field values
        max_length: Maximum string length (default 250)

    Returns:
        Dictionary with sanitized values
    """
    # Truncate long text fields
    text_fields = ["description", "interesting_fact"]
    for field in text_fields:
        if field in data and isinstance(data[field], str):
            if len(data[field]) > max_length:
                data[field] = data[field][: max_length - 3] + "..."

    # Convert empty airport_code to None (some cities don't have airports)
    if "airport_code" in data:
        code = data["airport_code"]
        if code is None or (isinstance(code, str) and len(code) < 3):
            data["airport_code"] = None

    return data


class GoogleProvider:
    """Google Gemini API provider for structured continent information."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize Google Gemini provider.

        Args:
            api_key: Google API key. If not provided, reads from env var.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"

    def get_model_identity(self) -> ModelIdentity:
        """
        Return hardcoded model identity for Google Gemini.

        Note: LLMs cannot reliably self-identify as they may have been trained
        on data from other models. Using hardcoded values ensures consistency.

        Returns:
            ModelIdentity with model_provider="Google" and model_name

        Example:
            >>> provider = GoogleProvider()
            >>> identity = provider.get_model_identity()
            >>> print(identity.model_provider)
            Google
        """
        return ModelIdentity(
            model_provider="Google",
            model_name=self.model,
        )

    def get_continent_info(self, continent_name: str) -> ContinentInfo:
        """
        Get structured continent information from Gemini.

        Args:
            continent_name: Name of the continent to query

        Returns:
            ContinentInfo with structured data

        Example:
            >>> provider = GoogleProvider()
            >>> info = provider.get_continent_info("Africa")
            >>> print(info.population)
            1400000000
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=(
                f"You are a helpful AI geography teacher. "
                f"Please provide the information on the continent of "
                f"{continent_name} with these fields:\n"
                "- description: less than 250 characters\n"
                "- area_sq_mile: total area in square miles (number)\n"
                "- area_sq_km: total area in square km (number)\n"
                "- population: total population of all countries (integer)\n"
                "- num_country: total number of sovereign nations in the "
                "continental region (integer)"
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ContinentInfo,
                max_output_tokens=500,
            ),
        )

        content = response.text or "{}"

        try:
            return ContinentInfo.model_validate_json(content)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Failed to parse continent info: {e}") from e

    def get_country_info(self, country_name: str) -> CountryInfo:
        """
        Get structured country information from Gemini.

        Args:
            country_name: Name of the country to query

        Returns:
            CountryInfo with structured data

        Example:
            >>> provider = GoogleProvider()
            >>> info = provider.get_country_info("Kenya")
            >>> print(info.population)
            54000000
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=(
                f"You are a helpful AI geography teacher knowledgeable on "
                f"world geography, continents and countries. "
                f"Please provide information on the country {country_name} "
                "in JSON format with these fields:\n"
                "- description: less than 250 characters\n"
                "- interesting_fact: less than 250 characters\n"
                "- area_sq_mile: area in square miles (number)\n"
                "- area_sq_km: area in square km (number)\n"
                "- population: total population (integer)\n"
                "- ppp: purchasing power parity in USD (number)\n"
                "- life_expectancy: in years (number)\n"
                "- travel_risk_level: US State Dept advisory in format "
                "'Level X: Description' where X is 1-4 "
                "(e.g., 'Level 2: Exercise Increased Caution')\n"
                "- global_peace_index_score: IEP score (number)\n"
                "- global_peace_index_rank: IEP rank (integer)\n"
                "- happiness_index_score: Oxford score (number)\n"
                "- happiness_index_rank: Oxford rank (integer)\n"
                "- gdp: in USD (number)\n"
                "- gdp_growth_rate: percentage (number)\n"
                "- inflation_rate: percentage (number)\n"
                "- unemployment_rate: percentage (number)\n"
                "- govt_debt: as percentage of GDP (number)\n"
                "- credit_rating: S&P rating (string)\n"
                "- poverty_rate: percentage (number)\n"
                "- gini_coefficient: inequality measure (number)\n"
                "- military_spending: as percentage of GDP (number)"
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=2000,
            ),
        )

        content = response.text or "{}"

        try:
            data = json.loads(content)
            data = _sanitize_city_data(data)
            return CountryInfo(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"\n[DEBUG] Raw JSON response:\n{content[:500]}...")
            raise ValueError(f"Failed to parse country info: {e}") from e

    def get_country_info_with_retry(self, country_name: str) -> CountryInfo:
        """
        Get country info with retry logic for transient failures.

        Args:
            country_name: Name of the country to query

        Returns:
            CountryInfo with structured data

        Raises:
            ValueError: After all retries exhausted
        """
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                return self.get_country_info(country_name)
            except ValueError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    print(f"    [Retry {attempt + 1}/{MAX_RETRIES}] {e}")
                    time.sleep(RETRY_DELAY)
        raise ValueError(f"Failed after {MAX_RETRIES} attempts: {last_error}")

    def get_cities_info(self, country_name: str) -> list[CityInfo]:
        """
        Get structured city information for a country from Gemini.

        Args:
            country_name: Name of the country to query cities for

        Returns:
            List of CityInfo with structured data (up to 5 cities)

        Example:
            >>> provider = GoogleProvider()
            >>> cities = provider.get_cities_info("Kenya")
            >>> print(len(cities))
            5
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=(
                f"You are a helpful AI geography teacher knowledgeable on "
                f"world geography, continents, countries, and cities. "
                f"Please list up to 5 most populous cities in {country_name} "
                "and return a JSON object with a 'cities' array. "
                "Each city should have these fields:\n"
                "- name: city name (string)\n"
                "- is_capital: whether capital city (boolean)\n"
                "- description: less than 250 characters\n"
                "- interesting_fact: less than 250 characters\n"
                "- area_sq_mile: area in square miles (number)\n"
                "- area_sq_km: area in square km (number)\n"
                "- population: total population (integer)\n"
                "- sci_score: EIU Safe Cities Index 0-100 or null\n"
                "- sci_rank: EIU rank or null\n"
                "- numbeo_si: Numbeo Safety Index 0-100 or null\n"
                "- numbeo_ci: Numbeo Crime Index 0-100 or null\n"
                "- airport_code: 3-letter IATA code for nearest airport"
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=4000,
            ),
        )

        content = response.text or '{"cities": []}'

        try:
            data = json.loads(content)
            # Handle both formats: direct list or {"cities": [...]}
            if isinstance(data, list):
                cities_data = data
            elif isinstance(data, dict) and "cities" in data:
                cities_data = data["cities"]
            else:
                raise ValueError(f"Unexpected cities format: {type(data)}")
            return [CityInfo(**_sanitize_city_data(city)) for city in cities_data]
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"\n[DEBUG] Raw cities JSON response:\n{content[:800]}...")
            raise ValueError(f"Failed to parse cities info: {e}") from e

    def get_cities_info_with_retry(self, country_name: str) -> list[CityInfo]:
        """
        Get cities info with retry logic for transient failures.

        Args:
            country_name: Name of the country to query cities for

        Returns:
            List of CityInfo with structured data

        Raises:
            ValueError: After all retries exhausted
        """
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                return self.get_cities_info(country_name)
            except ValueError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    print(f"    [Retry {attempt + 1}/{MAX_RETRIES}] {e}")
                    time.sleep(RETRY_DELAY)
        raise ValueError(f"Failed after {MAX_RETRIES} attempts: {last_error}")
