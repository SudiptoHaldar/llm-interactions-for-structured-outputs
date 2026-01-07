"""Tests for Cohere Command provider."""

import json
from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.providers.cohere_provider import (
    CohereProvider,
    _sanitize_json,
    _try_extract_json,
)


class TestSanitizeJson:
    """Tests for _sanitize_json helper function."""

    def test_removes_markdown_code_blocks(self) -> None:
        """Test removes markdown code block markers."""
        input_json = '```json\n{"key": "value"}\n```'
        result = _sanitize_json(input_json)
        assert result.strip() == '{"key": "value"}'

    def test_removes_trailing_commas(self) -> None:
        """Test removes trailing commas before closing braces."""
        input_json = '{"key": "value",}'
        result = _sanitize_json(input_json)
        assert result == '{"key": "value"}'

    def test_removes_commas_from_numbers(self) -> None:
        """Test removes commas from comma-separated numbers."""
        input_json = '{"population": 3,796,742}'
        result = _sanitize_json(input_json)
        assert result == '{"population": 3796742}'

    def test_handles_valid_json(self) -> None:
        """Test passes through valid JSON unchanged."""
        input_json = '{"key": "value", "num": 42}'
        result = _sanitize_json(input_json)
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["num"] == 42


class TestTryExtractJson:
    """Tests for _try_extract_json helper function."""

    def test_extracts_json_from_text(self) -> None:
        """Test extracts JSON object from surrounding text."""
        content = 'Here is the data: {"key": "value"} and more text'
        result = _try_extract_json(content)
        assert result == '{"key": "value"}'

    def test_returns_original_if_no_json(self) -> None:
        """Test returns original content if no JSON found."""
        content = "No JSON here"
        result = _try_extract_json(content)
        assert result == content


class TestCohereProvider:
    """Tests for CohereProvider."""

    @patch.dict("os.environ", {"CO_API_KEY": "test-key"})
    def test_init_with_env_var(self) -> None:
        """Test provider initializes with env var."""
        with patch("process_structured_output.providers.cohere_provider.cohere"):
            provider = CohereProvider()
            assert provider.api_key == "test-key"

    def test_init_with_explicit_key(self) -> None:
        """Test provider initializes with explicit key."""
        with patch("process_structured_output.providers.cohere_provider.cohere"):
            provider = CohereProvider(api_key="explicit-key")
            assert provider.api_key == "explicit-key"

    @patch("process_structured_output.providers.cohere_provider.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_raises_without_key(self, mock_load_dotenv: MagicMock) -> None:
        """Test provider raises error without API key."""
        with pytest.raises(ValueError, match="CO_API_KEY"):
            CohereProvider()

    @patch.dict("os.environ", {"CO_API_KEY": "test-key"})
    def test_get_model_identity_returns_hardcoded_values(self) -> None:
        """Test get_model_identity returns hardcoded provider and model name."""
        with patch(
            "process_structured_output.providers.cohere_provider.cohere"
        ):
            provider = CohereProvider()
            identity = provider.get_model_identity()

            # Hardcoded values - no API call made
            assert identity.model_provider == "Cohere"
            assert identity.model_name == "command-r-plus-08-2024"

    @patch.dict("os.environ", {"CO_API_KEY": "test-key"})
    def test_get_country_info_parses_json_response(self) -> None:
        """Test get_country_info parses JSON response."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = json.dumps({
            "description": "Test country",
            "interesting_fact": "A fun fact",
            "area_sq_mile": 356669.0,
            "area_sq_km": 923768.0,
            "population": 220000000,
            "ppp": 5500.0,
            "life_expectancy": 55.0,
            "travel_risk_level": "Level 3",
            "global_peace_index_score": 2.7,
            "global_peace_index_rank": 144,
            "happiness_index_score": 4.5,
            "happiness_index_rank": 99,
            "gdp": 450000000000.0,
            "gdp_growth_rate": 3.5,
            "inflation_rate": 18.0,
            "unemployment_rate": 5.0,
            "govt_debt": 38.0,
            "credit_rating": "B-",
            "poverty_rate": 40.0,
            "gini_coefficient": 35.0,
            "military_spending": 0.6,
        })
        mock_response.message.content = [mock_content]

        with patch(
            "process_structured_output.providers.cohere_provider.cohere"
        ) as mock_cohere:
            mock_client = MagicMock()
            mock_client.chat.return_value = mock_response
            mock_cohere.ClientV2.return_value = mock_client

            provider = CohereProvider()
            info = provider.get_country_info("Nigeria")

            assert info.description == "Test country"
            assert info.population == 220000000
            assert info.gdp == 450000000000.0

    @patch.dict("os.environ", {"CO_API_KEY": "test-key"})
    def test_get_country_info_raises_on_invalid_json(self) -> None:
        """Test get_country_info raises on invalid JSON response."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Not valid JSON at all"
        mock_response.message.content = [mock_content]

        with patch(
            "process_structured_output.providers.cohere_provider.cohere"
        ) as mock_cohere:
            mock_client = MagicMock()
            mock_client.chat.return_value = mock_response
            mock_cohere.ClientV2.return_value = mock_client

            provider = CohereProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_country_info("Nigeria")

    @patch.dict("os.environ", {"CO_API_KEY": "test-key"})
    def test_get_cities_info_parses_json_response(self) -> None:
        """Test get_cities_info parses JSON response."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = json.dumps({
            "cities": [
                {
                    "name": "Lagos",
                    "is_capital": False,
                    "description": "Economic hub",
                    "interesting_fact": "Most populous city",
                    "area_sq_mile": 452.0,
                    "area_sq_km": 1171.0,
                    "population": 15000000,
                    "sci_score": None,
                    "sci_rank": None,
                    "numbeo_si": 35.0,
                    "numbeo_ci": 65.0,
                    "airport_code": "LOS",
                }
            ]
        })
        mock_response.message.content = [mock_content]

        with patch(
            "process_structured_output.providers.cohere_provider.cohere"
        ) as mock_cohere:
            mock_client = MagicMock()
            mock_client.chat.return_value = mock_response
            mock_cohere.ClientV2.return_value = mock_client

            provider = CohereProvider()
            cities = provider.get_cities_info("Nigeria")

            assert len(cities) == 1
            assert cities[0].name == "Lagos"
            assert cities[0].is_capital is False
            assert cities[0].population == 15000000

    @patch.dict("os.environ", {"CO_API_KEY": "test-key"})
    def test_get_cities_info_raises_on_invalid_json(self) -> None:
        """Test get_cities_info raises on invalid JSON response."""
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Not valid JSON"
        mock_response.message.content = [mock_content]

        with patch(
            "process_structured_output.providers.cohere_provider.cohere"
        ) as mock_cohere:
            mock_client = MagicMock()
            mock_client.chat.return_value = mock_response
            mock_cohere.ClientV2.return_value = mock_client

            provider = CohereProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_cities_info("Nigeria")
