"""DeepSeek provider for structured outputs using OpenAI-compatible API."""

import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from process_structured_output.models.continent import ModelIdentity
from process_structured_output.models.country import CityInfo, CountryInfo
from process_structured_output.prompts import (
    get_cities_user_prompt,
    get_country_user_prompt,
    truncate_city_strings,
    truncate_country_strings,
)

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
        # CRITICAL: Must include "json" in prompt for DeepSeek JSON mode to work
        # The shared prompt includes "JSON" in the request
        prompt = get_country_user_prompt(country_name)

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
            # Truncate strings to enforce character limits
            data = truncate_country_strings(data)
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
        # CRITICAL: Must include "json" in prompt for DeepSeek JSON mode to work
        # The shared prompt includes "JSON" in the request
        prompt = get_cities_user_prompt(country_name)

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

            # Truncate strings to enforce character limits
            return [CityInfo(**truncate_city_strings(city)) for city in cities_data]
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
