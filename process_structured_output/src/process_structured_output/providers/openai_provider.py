"""OpenAI provider for structured outputs."""

import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from process_structured_output.models.continent import ContinentInfo, ModelIdentity


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
        Ask OpenAI which model is responding.

        Returns:
            ModelIdentity with model_provider and model_name

        Example:
            >>> provider = OpenAIProvider()
            >>> identity = provider.get_model_identity()
            >>> print(identity.model_provider)
            OpenAI
        """
        response = self.client.chat.completions.create(
            model=self.model,
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
            max_tokens=100,
        )

        content = response.choices[0].message.content or ""

        # Parse response: "Model Provider: OpenAI | Model Name: gpt-4o"
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
