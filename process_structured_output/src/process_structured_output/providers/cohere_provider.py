"""Cohere Command provider for structured outputs."""

import json
import os
import re
import time
from typing import Any

import cohere
from dotenv import load_dotenv
from pydantic import ValidationError

from process_structured_output.models.continent import ModelIdentity
from process_structured_output.models.country import CityInfo, CountryInfo


def _sanitize_json(content: str) -> str:
    """
    Sanitize JSON content to handle common LLM JSON issues.

    LLMs sometimes produce invalid JSON with:
    - Trailing commas
    - Single quotes instead of double quotes
    - Unquoted property names
    - JavaScript-style comments
    - Control characters
    - Markdown code blocks
    - Comma-separated numbers (e.g., 3,796,742 instead of 3796742)

    Args:
        content: Raw JSON string

    Returns:
        Sanitized JSON string
    """
    # Remove markdown code block markers if present
    sanitized = re.sub(r"^```(?:json)?\s*\n?", "", content, flags=re.MULTILINE)
    sanitized = re.sub(r"\n?```\s*$", "", sanitized, flags=re.MULTILINE)

    # Remove JavaScript-style comments (// and /* */)
    sanitized = re.sub(r"//.*?$", "", sanitized, flags=re.MULTILINE)
    sanitized = re.sub(r"/\*.*?\*/", "", sanitized, flags=re.DOTALL)

    # Remove control characters (except newlines and tabs)
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", sanitized)

    # Remove commas from numbers (e.g., 3,796,742 -> 3796742)
    def remove_number_commas(match: re.Match[str]) -> str:
        prefix = match.group(1)
        number = match.group(2).replace(",", "")
        return prefix + number

    sanitized = re.sub(
        r'(:\s*)(\d{1,3}(?:,\d{3})+)(?=[,\s\n\r}\]])',
        remove_number_commas,
        sanitized,
    )

    # Remove trailing commas before closing braces/brackets
    sanitized = re.sub(r",\s*([}\]])", r"\1", sanitized)

    # Quote unquoted property names
    sanitized = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', sanitized)

    return sanitized


def _try_extract_json(content: str) -> str:
    """
    Try to extract valid JSON from content that may have surrounding text.

    Args:
        content: Raw content that may contain JSON

    Returns:
        Extracted JSON string
    """
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        return content[start : end + 1]
    return content


# Maximum retries for transient LLM JSON parsing failures
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
RATE_LIMIT_DELAY = 10.0  # seconds - longer delay for 429 errors


def _build_country_schema() -> dict[str, Any]:
    """Build the JSON schema for country info extraction."""
    return {
        "type": "object",
        "required": [
            "description",
            "interesting_fact",
            "area_sq_mile",
            "area_sq_km",
            "population",
            "ppp",
            "life_expectancy",
            "travel_risk_level",
            "global_peace_index_score",
            "global_peace_index_rank",
            "happiness_index_score",
            "happiness_index_rank",
            "gdp",
            "gdp_growth_rate",
            "inflation_rate",
            "unemployment_rate",
            "govt_debt",
            "credit_rating",
            "poverty_rate",
            "gini_coefficient",
            "military_spending",
        ],
        "properties": {
            "description": {"type": "string"},
            "interesting_fact": {"type": "string"},
            "area_sq_mile": {"type": "number"},
            "area_sq_km": {"type": "number"},
            "population": {"type": "integer"},
            "ppp": {"type": "number"},
            "life_expectancy": {"type": "number"},
            "travel_risk_level": {"type": "string"},
            "global_peace_index_score": {"type": "number"},
            "global_peace_index_rank": {"type": "integer"},
            "happiness_index_score": {"type": "number"},
            "happiness_index_rank": {"type": "integer"},
            "gdp": {"type": "number"},
            "gdp_growth_rate": {"type": "number"},
            "inflation_rate": {"type": "number"},
            "unemployment_rate": {"type": "number"},
            "govt_debt": {"type": "number"},
            "credit_rating": {"type": "string"},
            "poverty_rate": {"type": "number"},
            "gini_coefficient": {"type": "number"},
            "military_spending": {"type": "number"},
        },
    }


def _build_cities_schema() -> dict[str, Any]:
    """Build the JSON schema for cities info extraction."""
    city_schema = {
        "type": "object",
        "required": [
            "name",
            "is_capital",
            "description",
            "interesting_fact",
            "area_sq_mile",
            "area_sq_km",
            "population",
            "airport_code",
        ],
        "properties": {
            "name": {"type": "string"},
            "is_capital": {"type": "boolean"},
            "description": {"type": "string"},
            "interesting_fact": {"type": "string"},
            "area_sq_mile": {"type": "number"},
            "area_sq_km": {"type": "number"},
            "population": {"type": "integer"},
            "sci_score": {"type": ["number", "null"]},
            "sci_rank": {"type": ["integer", "null"]},
            "numbeo_si": {"type": ["number", "null"]},
            "numbeo_ci": {"type": ["number", "null"]},
            "airport_code": {"type": "string"},
        },
    }

    return {
        "type": "object",
        "required": ["cities"],
        "properties": {
            "cities": {
                "type": "array",
                "items": city_schema,
            },
        },
    }


class CohereProvider:
    """Cohere Command API provider for structured country information."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize Cohere provider.

        Args:
            api_key: Cohere API key. If not provided, reads from env var.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("CO_API_KEY")
        if not self.api_key:
            raise ValueError("CO_API_KEY environment variable not set")
        self.client = cohere.ClientV2(api_key=self.api_key)
        self.model = "command-r-plus-08-2024"

    def get_model_identity(self) -> ModelIdentity:
        """
        Return hardcoded model identity for Cohere Command.

        Note: LLMs cannot reliably self-identify as they may have been trained
        on data from other models. Using hardcoded values ensures consistency.

        Returns:
            ModelIdentity with model_provider="Cohere" and model_name
        """
        return ModelIdentity(
            model_provider="Cohere",
            model_name=self.model,
        )

    def get_country_info(self, country_name: str) -> CountryInfo:
        """
        Get structured country information from Cohere using JSON schema.

        Args:
            country_name: Name of the country to query

        Returns:
            CountryInfo with structured data
        """
        messages_list = [
            {
                "role": "user",
                "content": (
                    f"You are a helpful AI geography teacher knowledgeable on "
                    f"world geography, continents and countries. Generate a JSON "
                    f"with comprehensive information about {country_name}. "
                    f"Include accurate geographic, economic, and social data. "
                    f"All text fields should be under 250 characters."
                ),
            }
        ]
        response_format = {
            "type": "json_object",
            "schema": _build_country_schema(),
        }
        response = self.client.chat(
            model=self.model,
            messages=messages_list,  # type: ignore[arg-type]
            response_format=response_format,  # type: ignore[arg-type]
        )

        content = "{}"
        if response.message.content:
            first_item = response.message.content[0]
            if hasattr(first_item, "text"):
                content = first_item.text  # type: ignore[union-attr]

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
        Get structured city information for a country from Cohere using JSON schema.

        Args:
            country_name: Name of the country to query cities for

        Returns:
            List of CityInfo with structured data (up to 5 cities)
        """
        messages_list = [
            {
                "role": "user",
                "content": (
                    f"You are a helpful AI geography teacher knowledgeable on "
                    f"world geography, continents, countries, and cities. "
                    f"Generate a JSON with information about up to 5 most "
                    f"populous cities in {country_name}. Include accurate data "
                    f"for each city. All text fields should be under 250 chars."
                ),
            }
        ]
        response_format = {
            "type": "json_object",
            "schema": _build_cities_schema(),
        }
        response = self.client.chat(
            model=self.model,
            messages=messages_list,  # type: ignore[arg-type]
            response_format=response_format,  # type: ignore[arg-type]
        )

        content = '{"cities": []}'
        if response.message.content:
            first_item = response.message.content[0]
            if hasattr(first_item, "text"):
                content = first_item.text  # type: ignore[union-attr]

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
