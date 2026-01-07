"""Tests for Anthropic Claude provider."""

from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.providers.anthropic_provider import AnthropicProvider


class TestAnthropicProvider:
    """Tests for AnthropicProvider."""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_init_with_env_var(self) -> None:
        """Test provider initializes with env var."""
        with patch(
            "process_structured_output.providers.anthropic_provider.Anthropic"
        ):
            provider = AnthropicProvider()
            assert provider.api_key == "test-key"

    def test_init_with_explicit_key(self) -> None:
        """Test provider initializes with explicit key."""
        with patch(
            "process_structured_output.providers.anthropic_provider.Anthropic"
        ):
            provider = AnthropicProvider(api_key="explicit-key")
            assert provider.api_key == "explicit-key"

    @patch("process_structured_output.providers.anthropic_provider.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_raises_without_key(self, mock_load_dotenv: MagicMock) -> None:
        """Test provider raises error without API key."""
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            AnthropicProvider()

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_model_identity_returns_hardcoded_values(self) -> None:
        """Test get_model_identity returns hardcoded provider and model name."""
        with patch(
            "process_structured_output.providers.anthropic_provider.Anthropic"
        ):
            provider = AnthropicProvider()
            identity = provider.get_model_identity()

            # Hardcoded values - no API call made
            assert identity.model_provider == "Anthropic"
            assert identity.model_name == "claude-haiku-4-5"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_country_info_parses_tool_response(self) -> None:
        """Test get_country_info parses tool use response."""
        mock_response = MagicMock()
        mock_tool_use = MagicMock()
        mock_tool_use.type = "tool_use"
        mock_tool_use.name = "record_country_info"
        mock_tool_use.input = {
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
        }
        mock_response.content = [mock_tool_use]

        with patch(
            "process_structured_output.providers.anthropic_provider.Anthropic"
        ) as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            provider = AnthropicProvider()
            info = provider.get_country_info("Nigeria")

            assert info.description == "Test country"
            assert info.population == 220000000
            assert info.gdp == 450000000000.0

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_country_info_raises_when_no_tool_use(self) -> None:
        """Test get_country_info raises when Claude doesn't use tool."""
        mock_response = MagicMock()
        mock_text = MagicMock()
        mock_text.type = "text"
        mock_response.content = [mock_text]

        with patch(
            "process_structured_output.providers.anthropic_provider.Anthropic"
        ) as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            provider = AnthropicProvider()
            with pytest.raises(ValueError, match="did not use"):
                provider.get_country_info("Nigeria")

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_cities_info_parses_tool_response(self) -> None:
        """Test get_cities_info parses tool use response."""
        mock_response = MagicMock()
        mock_tool_use = MagicMock()
        mock_tool_use.type = "tool_use"
        mock_tool_use.name = "record_cities_info"
        mock_tool_use.input = {
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
        }
        mock_response.content = [mock_tool_use]

        with patch(
            "process_structured_output.providers.anthropic_provider.Anthropic"
        ) as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            provider = AnthropicProvider()
            cities = provider.get_cities_info("Nigeria")

            assert len(cities) == 1
            assert cities[0].name == "Lagos"
            assert cities[0].is_capital is False
            assert cities[0].population == 15000000

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_cities_info_raises_when_no_tool_use(self) -> None:
        """Test get_cities_info raises when Claude doesn't use tool."""
        mock_response = MagicMock()
        mock_text = MagicMock()
        mock_text.type = "text"
        mock_response.content = [mock_text]

        with patch(
            "process_structured_output.providers.anthropic_provider.Anthropic"
        ) as mock_anthropic:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            provider = AnthropicProvider()
            with pytest.raises(ValueError, match="did not use"):
                provider.get_cities_info("Nigeria")
