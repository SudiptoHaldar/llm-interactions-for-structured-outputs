"""Google Gemini provider for structured outputs."""

import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from process_structured_output.models.continent import ContinentInfo, ModelIdentity


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
        Ask Gemini which model is responding.

        Returns:
            ModelIdentity with model_provider and model_name

        Example:
            >>> provider = GoogleProvider()
            >>> identity = provider.get_model_identity()
            >>> print(identity.model_provider)
            Google
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=(
                "Who is answering this question? Response should be in the "
                "form of 'Model Provider: {model_provider} | "
                "Model Name: {model_name}'"
            ),
            config=types.GenerateContentConfig(
                max_output_tokens=100,
            ),
        )

        content = response.text or ""

        # Parse response: "Model Provider: Google | Model Name: gemini-2.5-flash"
        pattern = r"Model Provider:\s*([^|]+)\s*\|\s*Model Name:\s*(.+)"
        match = re.search(pattern, content, re.IGNORECASE)

        if not match:
            raise ValueError(f"Could not parse model identity from: {content}")

        return ModelIdentity(
            model_provider=match.group(1).strip(),
            model_name=match.group(2).strip(),
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
