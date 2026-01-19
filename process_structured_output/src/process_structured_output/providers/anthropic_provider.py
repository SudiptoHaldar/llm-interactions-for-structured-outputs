"""Anthropic Claude provider for structured outputs."""

import os
import time

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from process_structured_output.models.continent import ModelIdentity
from process_structured_output.models.country import CityInfo, CountryInfo
from process_structured_output.prompts import (
    COUNTRY_SYSTEM_PROMPT,
    get_cities_tool_schema,
    get_country_tool_schema,
    truncate_city_strings,
    truncate_country_strings,
)

# Maximum retries for transient LLM failures
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds


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
        Return hardcoded model identity for Anthropic Claude.

        Note: LLMs cannot reliably self-identify as they may have been trained
        on data from other models. Using hardcoded values ensures consistency.

        Returns:
            ModelIdentity with model_provider="Anthropic" and model_name
        """
        return ModelIdentity(
            model_provider="Anthropic",
            model_name=self.model,
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
            tools=[get_country_tool_schema()],
            tool_choice={"type": "tool", "name": "record_country_info"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"{COUNTRY_SYSTEM_PROMPT} Please provide comprehensive "
                        f"information about {country_name} using the "
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
                    # Truncate strings to enforce character limits
                    data = truncate_country_strings(content_block.input)
                    return CountryInfo(**data)
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
            tools=[get_cities_tool_schema()],
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
                    # Truncate strings to enforce character limits
                    cities_data = [truncate_city_strings(c) for c in cities_data]
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
