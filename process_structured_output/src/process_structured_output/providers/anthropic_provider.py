"""Anthropic Claude provider for structured outputs."""

import os
import re
import time
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from process_structured_output.models.continent import ModelIdentity
from process_structured_output.models.country import CityInfo, CountryInfo

# Maximum retries for transient LLM failures
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds


def _build_country_tool() -> dict[str, Any]:
    """Build the tool definition for country info extraction."""
    return {
        "name": "record_country_info",
        "description": "Records structured information about a country",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Brief description (max 250 chars)",
                },
                "interesting_fact": {
                    "type": "string",
                    "description": "Notable fact (max 250 chars)",
                },
                "area_sq_mile": {
                    "type": "number",
                    "description": "Area in square miles",
                },
                "area_sq_km": {
                    "type": "number",
                    "description": "Area in square kilometers",
                },
                "population": {
                    "type": "integer",
                    "description": "Total population",
                },
                "ppp": {
                    "type": "number",
                    "description": "Purchasing power parity in USD",
                },
                "life_expectancy": {
                    "type": "number",
                    "description": "Life expectancy in years",
                },
                "travel_risk_level": {
                    "type": "string",
                    "description": "US State Dept advisory level",
                },
                "global_peace_index_score": {
                    "type": "number",
                    "description": "GPI score (IEP)",
                },
                "global_peace_index_rank": {
                    "type": "integer",
                    "description": "GPI rank",
                },
                "happiness_index_score": {
                    "type": "number",
                    "description": "World Happiness score",
                },
                "happiness_index_rank": {
                    "type": "integer",
                    "description": "World Happiness rank",
                },
                "gdp": {
                    "type": "number",
                    "description": "GDP in USD",
                },
                "gdp_growth_rate": {
                    "type": "number",
                    "description": "GDP growth rate %",
                },
                "inflation_rate": {
                    "type": "number",
                    "description": "Inflation rate %",
                },
                "unemployment_rate": {
                    "type": "number",
                    "description": "Unemployment rate %",
                },
                "govt_debt": {
                    "type": "number",
                    "description": "Government debt as % of GDP",
                },
                "credit_rating": {
                    "type": "string",
                    "description": "S&P credit rating",
                },
                "poverty_rate": {
                    "type": "number",
                    "description": "Poverty rate %",
                },
                "gini_coefficient": {
                    "type": "number",
                    "description": "Gini coefficient (0-100)",
                },
                "military_spending": {
                    "type": "number",
                    "description": "Military spending as % of GDP",
                },
            },
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
        },
    }


def _build_cities_tool() -> dict[str, Any]:
    """Build the tool definition for cities info extraction."""
    city_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "City name",
            },
            "is_capital": {
                "type": "boolean",
                "description": "Whether this is the capital city",
            },
            "description": {
                "type": "string",
                "description": "Brief description (max 250 chars)",
            },
            "interesting_fact": {
                "type": "string",
                "description": "Notable fact (max 250 chars)",
            },
            "area_sq_mile": {
                "type": "number",
                "description": "Area in square miles",
            },
            "area_sq_km": {
                "type": "number",
                "description": "Area in square kilometers",
            },
            "population": {
                "type": "integer",
                "description": "Total population",
            },
            "sci_score": {
                "type": ["number", "null"],
                "description": "EIU Safe Cities Index score (0-100)",
            },
            "sci_rank": {
                "type": ["integer", "null"],
                "description": "EIU Safe Cities Index rank",
            },
            "numbeo_si": {
                "type": ["number", "null"],
                "description": "Numbeo Safety Index (0-100)",
            },
            "numbeo_ci": {
                "type": ["number", "null"],
                "description": "Numbeo Crime Index (0-100)",
            },
            "airport_code": {
                "type": "string",
                "description": "3-letter IATA airport code",
            },
        },
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
    }

    return {
        "name": "record_cities_info",
        "description": "Records structured information about cities in a country",
        "input_schema": {
            "type": "object",
            "properties": {
                "cities": {
                    "type": "array",
                    "items": city_schema,
                    "description": "List of up to 5 most populous cities",
                },
            },
            "required": ["cities"],
        },
    }


class AnthropicProvider:
    """Anthropic Claude API provider for structured country information."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key. If not provided, reads from env var.
        """
        load_dotenv()
        if api_key:
            self.client = Anthropic(api_key=api_key)
            self.api_key = api_key
        else:
            # Anthropic client auto-reads ANTHROPIC_API_KEY env var
            env_key = os.getenv("ANTHROPIC_API_KEY")
            if not env_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.api_key = env_key
            self.client = Anthropic()
        self.model = "claude-haiku-4-5"

    def get_model_identity(self) -> ModelIdentity:
        """
        Ask Claude which model is responding.

        Returns:
            ModelIdentity with model_provider and model_name
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Who is answering this question? Response should be in the "
                        "form of 'Model Provider: {model_provider} | "
                        "Model Name: {model_name}'"
                    ),
                }
            ],
        )

        content = response.content[0].text if response.content else ""  # type: ignore[union-attr]

        # Parse response: "Model Provider: Anthropic | Model Name: claude-haiku"
        pattern = r"Model Provider:\s*([^|]+)\s*\|\s*Model Name:\s*(.+)"
        match = re.search(pattern, content, re.IGNORECASE)

        if not match:
            raise ValueError(f"Could not parse model identity from: {content}")

        return ModelIdentity(
            model_provider=match.group(1).strip(),
            model_name=match.group(2).strip(),
        )

    def get_country_info(self, country_name: str) -> CountryInfo:
        """
        Get structured country information from Claude using tool use.

        Args:
            country_name: Name of the country to query

        Returns:
            CountryInfo with structured data
        """
        response = self.client.messages.create(  # type: ignore[call-overload]
            model=self.model,
            max_tokens=1500,
            tools=[_build_country_tool()],
            tool_choice={"type": "tool", "name": "record_country_info"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a helpful AI geography teacher knowledgeable on "
                        f"world geography, continents and countries. Please provide "
                        f"comprehensive information about {country_name} using the "
                        f"record_country_info tool. Include accurate geographic, "
                        f"economic, and social data."
                    ),
                }
            ],
        )

        # Extract tool use result
        for content_block in response.content:
            is_tool_use = content_block.type == "tool_use"
            is_country_tool = content_block.name == "record_country_info"
            if is_tool_use and is_country_tool:
                try:
                    return CountryInfo(**content_block.input)
                except ValidationError as e:
                    raise ValueError(f"Failed to validate country info: {e}") from e

        raise ValueError("Claude did not use the record_country_info tool")

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
        raise ValueError(f"Failed after {MAX_RETRIES} attempts: {last_error}")

    def get_cities_info(self, country_name: str) -> list[CityInfo]:
        """
        Get structured city information for a country from Claude using tool use.

        Args:
            country_name: Name of the country to query cities for

        Returns:
            List of CityInfo with structured data (up to 5 cities)
        """
        response = self.client.messages.create(  # type: ignore[call-overload]
            model=self.model,
            max_tokens=3000,
            tools=[_build_cities_tool()],
            tool_choice={"type": "tool", "name": "record_cities_info"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a helpful AI geography teacher knowledgeable on "
                        f"world geography, continents, countries, and cities. Please "
                        f"list up to 5 most populous cities in {country_name} using "
                        f"the record_cities_info tool. Include accurate data."
                    ),
                }
            ],
        )

        # Extract tool use result
        for content_block in response.content:
            is_tool_use = content_block.type == "tool_use"
            is_cities_tool = content_block.name == "record_cities_info"
            if is_tool_use and is_cities_tool:
                try:
                    cities_data = content_block.input.get("cities", [])
                    return [CityInfo(**city) for city in cities_data]
                except ValidationError as e:
                    raise ValueError(f"Failed to validate cities info: {e}") from e

        raise ValueError("Claude did not use the record_cities_info tool")

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
        raise ValueError(f"Failed after {MAX_RETRIES} attempts: {last_error}")
