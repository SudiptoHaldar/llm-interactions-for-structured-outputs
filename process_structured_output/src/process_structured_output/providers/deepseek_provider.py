"""DeepSeek provider for structured outputs using OpenAI-compatible API."""

import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from process_structured_output.models.continent import ModelIdentity
from process_structured_output.models.country import CityInfo, CountryInfo

# Reuse JSON sanitization helpers from cohere_provider
from process_structured_output.providers.cohere_provider import (
    _sanitize_json,
    _try_extract_json,
)

MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
RATE_LIMIT_DELAY = 10.0  # seconds for 429 errors


class DeepSeekProvider:
    """DeepSeek API provider using OpenAI-compatible interface."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize DeepSeek provider.

        Args:
            api_key: DeepSeek API key. If not provided, reads from env var.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )
        self.model = "deepseek-chat"

    def get_model_identity(self) -> ModelIdentity:
        """
        Return hardcoded model identity for DeepSeek.

        Note: LLMs cannot reliably self-identify as they may have been trained
        on data from other models. DeepSeek sometimes incorrectly identifies
        as "Google Gemini" when asked. Using hardcoded values ensures consistency.

        Returns:
            ModelIdentity with model_provider="DeepSeek" and model_name
        """
        return ModelIdentity(
            model_provider="DeepSeek",
            model_name=self.model,
        )

    def get_country_info(self, country_name: str) -> CountryInfo:
        """
        Get structured country information from DeepSeek using JSON mode.

        Args:
            country_name: Name of the country to query

        Returns:
            CountryInfo with structured data
        """
        # CRITICAL: Must include "json" in prompt for JSON mode to work
        prompt = (
            f"You are a helpful AI geography teacher knowledgeable on world "
            f"geography, continents and countries. Generate a JSON with "
            f"comprehensive information about {country_name}. Include accurate "
            f"geographic, economic, and social data. All text fields should be "
            f"under 250 characters.\n\n"
            f"Return a JSON object with these exact fields:\n"
            f"- description (string): Brief description of the country\n"
            f"- interesting_fact (string): An interesting fact about the country\n"
            f"- area_sq_mile (number): Area in square miles\n"
            f"- area_sq_km (number): Area in square kilometers\n"
            f"- population (integer): Total population\n"
            f"- ppp (number): Purchasing Power Parity in USD\n"
            f"- life_expectancy (number): Average life expectancy in years\n"
            f"- travel_risk_level (string): Travel risk (Low/Medium/High/Very High)\n"
            f"- global_peace_index_score (number): GPI score (1-5, lower=peaceful)\n"
            f"- global_peace_index_rank (integer): GPI ranking among countries\n"
            f"- happiness_index_score (number): World Happiness Report score (0-10)\n"
            f"- happiness_index_rank (integer): Happiness ranking among countries\n"
            f"- gdp (number): Gross Domestic Product in USD\n"
            f"- gdp_growth_rate (number): Annual GDP growth rate percentage\n"
            f"- inflation_rate (number): Annual inflation rate percentage\n"
            f"- unemployment_rate (number): Unemployment rate percentage\n"
            f"- govt_debt (number): Government debt as percentage of GDP\n"
            f"- credit_rating (string): Sovereign credit rating (e.g., AAA, BBB-)\n"
            f"- poverty_rate (number): Percentage of population below poverty line\n"
            f"- gini_coefficient (number): Income inequality measure (0-100)\n"
            f"- military_spending (number): Military spending as percentage of GDP"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"

        # Handle empty content
        if not content.strip() or content.strip() == "{}":
            raise ValueError("Empty JSON response from DeepSeek API")

        try:
            extracted = _try_extract_json(content)
            sanitized = _sanitize_json(extracted)
            data = json.loads(sanitized)
            return CountryInfo(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"\n[DEBUG] Raw JSON response:\n{content[:1000]}")
            raise ValueError(f"Failed to parse country info: {e}") from e

    def get_country_info_with_retry(self, country_name: str) -> CountryInfo:
        """Get country info with retry logic for transient failures."""
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                return self.get_country_info(country_name)
            except ValueError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    print(f"    [Retry {attempt + 1}/{MAX_RETRIES}] {e}")
                    time.sleep(RETRY_DELAY)
            except Exception as e:
                # Handle rate limits (429) and other API errors
                last_error = e
                if "429" in str(e) or "rate" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        print(f"    [Rate limit, waiting {RATE_LIMIT_DELAY}s...]")
                        time.sleep(RATE_LIMIT_DELAY)
                elif attempt < MAX_RETRIES - 1:
                    print(f"    [Retry {attempt + 1}/{MAX_RETRIES}] {e}")
                    time.sleep(RETRY_DELAY)
        raise ValueError(f"Failed after {MAX_RETRIES} attempts: {last_error}")

    def get_cities_info(self, country_name: str) -> list[CityInfo]:
        """
        Get structured city information for a country using JSON mode.

        Args:
            country_name: Name of the country to query cities for

        Returns:
            List of CityInfo with structured data (up to 5 cities)
        """
        # CRITICAL: Must include "json" in prompt for JSON mode to work
        prompt = (
            f"You are a helpful AI geography teacher knowledgeable on world "
            f"geography, continents, countries, and cities. Generate a JSON with "
            f"information about up to 5 most populous cities in {country_name}. "
            f"Include accurate data for each city. All text fields should be "
            f"under 250 characters.\n\n"
            f'Return a JSON object with a "cities" array containing objects '
            f"with these fields:\n"
            f"- name (string): City name\n"
            f"- is_capital (boolean): Whether this is the capital city\n"
            f"- description (string): Brief description of the city\n"
            f"- interesting_fact (string): An interesting fact about the city\n"
            f"- area_sq_mile (number): City area in square miles\n"
            f"- area_sq_km (number): City area in square kilometers\n"
            f"- population (integer): City population\n"
            f"- sci_score (number or null): Safe Cities Index score if available\n"
            f"- sci_rank (integer or null): Safe Cities Index rank if available\n"
            f"- numbeo_si (number or null): Numbeo Safety Index if available\n"
            f"- numbeo_ci (number or null): Numbeo Crime Index if available\n"
            f"- airport_code (string): Main airport IATA code (e.g., JFK, LAX)"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or '{"cities": []}'

        # Handle empty content
        if not content.strip():
            raise ValueError("Empty JSON response from DeepSeek API")

        try:
            extracted = _try_extract_json(content)
            sanitized = _sanitize_json(extracted)
            data = json.loads(sanitized)
            # Handle both formats: direct list or {"cities": [...]}
            if isinstance(data, list):
                cities_data = data
            elif isinstance(data, dict) and "cities" in data:
                cities_data = data["cities"]
            else:
                raise ValueError(f"Unexpected cities format: {type(data)}")

            return [CityInfo(**city) for city in cities_data]
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"\n[DEBUG] Raw JSON response:\n{content[:1000]}")
            raise ValueError(f"Failed to parse cities info: {e}") from e

    def get_cities_info_with_retry(self, country_name: str) -> list[CityInfo]:
        """Get cities info with retry logic for transient failures."""
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                return self.get_cities_info(country_name)
            except ValueError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    print(f"    [Retry {attempt + 1}/{MAX_RETRIES}] {e}")
                    time.sleep(RETRY_DELAY)
            except Exception as e:
                # Handle rate limits (429) and other API errors
                last_error = e
                if "429" in str(e) or "rate" in str(e).lower():
                    if attempt < MAX_RETRIES - 1:
                        print(f"    [Rate limit, waiting {RATE_LIMIT_DELAY}s...]")
                        time.sleep(RATE_LIMIT_DELAY)
                elif attempt < MAX_RETRIES - 1:
                    print(f"    [Retry {attempt + 1}/{MAX_RETRIES}] {e}")
                    time.sleep(RETRY_DELAY)
        raise ValueError(f"Failed after {MAX_RETRIES} attempts: {last_error}")
