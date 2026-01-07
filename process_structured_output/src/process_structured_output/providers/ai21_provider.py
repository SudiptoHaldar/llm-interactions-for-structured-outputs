"""AI21 Jamba provider for structured outputs."""

import json
import os
import re
import time

from ai21 import AI21Client
from ai21.models.chat import ChatMessage
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
    # Matches: colon, optional space, then digits with commas (number format)
    # Uses a function to remove commas only from the numeric part
    def remove_number_commas(match: re.Match[str]) -> str:
        prefix = match.group(1)  # ": " part
        number = match.group(2).replace(",", "")  # Remove commas from number
        return prefix + number

    sanitized = re.sub(
        r'(:\s*)(\d{1,3}(?:,\d{3})+)(?=[,\s\n\r}\]])',
        remove_number_commas,
        sanitized,
    )

    # Remove trailing commas before closing braces/brackets
    # Matches: comma, optional whitespace/newlines, then } or ]
    sanitized = re.sub(r",\s*([}\]])", r"\1", sanitized)

    # Quote unquoted property names (handles: {key: "value"} -> {"key": "value"})
    # This matches word characters followed by colon, not already quoted
    # More robust pattern that handles newlines
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
    # Try to find JSON object boundaries
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        return content[start : end + 1]
    return content


# Maximum retries for transient LLM JSON parsing failures
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds


class AI21Provider:
    """AI21 Jamba API provider for structured country information."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize AI21 provider.

        Args:
            api_key: AI21 API key. If not provided, reads from env var.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("AI21_API_KEY")
        if not self.api_key:
            raise ValueError("AI21_API_KEY environment variable not set")
        self.client = AI21Client(api_key=self.api_key)
        self.model = "jamba-mini"

    def get_model_identity(self) -> ModelIdentity:
        """
        Return hardcoded model identity for AI21 Jamba.

        Note: LLMs cannot reliably self-identify as they may have been trained
        on data from other models. Using hardcoded values ensures consistency.

        Returns:
            ModelIdentity with model_provider="AI21" and model_name

        Example:
            >>> provider = AI21Provider()
            >>> identity = provider.get_model_identity()
            >>> print(identity.model_provider)
            AI21
        """
        return ModelIdentity(
            model_provider="AI21",
            model_name=self.model,
        )

    def get_country_info(self, country_name: str) -> CountryInfo:
        """
        Get structured country information from AI21.

        Args:
            country_name: Name of the country to query

        Returns:
            CountryInfo with structured data

        Example:
            >>> provider = AI21Provider()
            >>> info = provider.get_country_info("Nigeria")
            >>> print(info.population)
            220000000
        """
        response = self.client.chat.completions.create(
            messages=[
                ChatMessage(
                    role="system",
                    content=(
                        "You are a helpful AI geography teacher knowledgeable on "
                        "world geography, continents and countries. Respond with "
                        "accurate geographic and economic data in JSON format."
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
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
                        "(e.g., 'Level 3: Reconsider Travel')\n"
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
                ),
            ],
            model=self.model,
            response_format={"type": "json_object"},
            max_tokens=1000,
        )

        content = response.choices[0].message.content or "{}"

        try:
            extracted = _try_extract_json(content)
            sanitized = _sanitize_json(extracted)
            data = json.loads(sanitized)
            return CountryInfo(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Show raw content for debugging
            print(f"\n[DEBUG] Raw JSON response:\n{content[:1000]}")
            print(f"\n[DEBUG] Sanitized JSON:\n{sanitized[:1000]}")
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
        Get structured city information for a country from AI21.

        Args:
            country_name: Name of the country to query cities for

        Returns:
            List of CityInfo with structured data (up to 5 cities)

        Example:
            >>> provider = AI21Provider()
            >>> cities = provider.get_cities_info("Nigeria")
            >>> print(len(cities))
            5
        """
        response = self.client.chat.completions.create(
            messages=[
                ChatMessage(
                    role="system",
                    content=(
                        "You are a helpful AI geography teacher knowledgeable on "
                        "world geography, continents, countries, and cities. "
                        "Respond with accurate data in JSON format."
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"Please list up to 5 most populous cities in {country_name} "
                        "and return information in JSON format with a 'cities' array. "
                        "Each city should have:\n"
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
                ),
            ],
            model=self.model,
            response_format={"type": "json_object"},
            max_tokens=2000,
        )

        content = response.choices[0].message.content or '{"cities": []}'

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
