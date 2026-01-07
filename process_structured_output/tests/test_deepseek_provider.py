"""Tests for DeepSeek provider using OpenAI-compatible API."""

import json
from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.providers.deepseek_provider import (
    MAX_RETRIES,
    RATE_LIMIT_DELAY,
    RETRY_DELAY,
    DeepSeekProvider,
)


class TestDeepSeekProviderInit:
    """Tests for DeepSeekProvider initialization."""

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_init_with_env_var(self) -> None:
        """Test provider initializes with env var."""
        with patch("process_structured_output.providers.deepseek_provider.OpenAI"):
            provider = DeepSeekProvider()
            assert provider.api_key == "test-key"
            assert provider.model == "deepseek-chat"

    def test_init_with_explicit_key(self) -> None:
        """Test provider initializes with explicit key."""
        with patch("process_structured_output.providers.deepseek_provider.OpenAI"):
            provider = DeepSeekProvider(api_key="explicit-key")
            assert provider.api_key == "explicit-key"
            assert provider.model == "deepseek-chat"

    @patch("process_structured_output.providers.deepseek_provider.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_raises_without_key(self, mock_load_dotenv: MagicMock) -> None:
        """Test provider raises error without API key."""
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            DeepSeekProvider()

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_init_sets_correct_base_url(self) -> None:
        """Test provider uses correct DeepSeek base URL."""
        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            DeepSeekProvider()
            mock_openai.assert_called_once_with(
                api_key="test-key",
                base_url="https://api.deepseek.com",
            )


class TestGetModelIdentity:
    """Tests for get_model_identity method."""

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_get_model_identity_returns_hardcoded_values(self) -> None:
        """Test get_model_identity returns hardcoded provider and model name."""
        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ):
            provider = DeepSeekProvider()
            identity = provider.get_model_identity()

            # Hardcoded values - no API call made
            assert identity.model_provider == "DeepSeek"
            assert identity.model_name == "deepseek-chat"


class TestGetCountryInfo:
    """Tests for get_country_info method."""

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_get_country_info_parses_json_response(self) -> None:
        """Test get_country_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
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

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            info = provider.get_country_info("Poland")

            assert info.description == "Test country"
            assert info.population == 220000000
            assert info.gdp == 450000000000.0

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_get_country_info_uses_json_mode(self) -> None:
        """Test get_country_info uses JSON response format."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "description": "Test",
            "interesting_fact": "Fact",
            "area_sq_mile": 100.0,
            "area_sq_km": 259.0,
            "population": 1000000,
            "ppp": 1000.0,
            "life_expectancy": 75.0,
            "travel_risk_level": "Low",
            "global_peace_index_score": 1.5,
            "global_peace_index_rank": 20,
            "happiness_index_score": 6.5,
            "happiness_index_rank": 25,
            "gdp": 100000000.0,
            "gdp_growth_rate": 2.0,
            "inflation_rate": 2.0,
            "unemployment_rate": 5.0,
            "govt_debt": 50.0,
            "credit_rating": "AA",
            "poverty_rate": 10.0,
            "gini_coefficient": 30.0,
            "military_spending": 2.0,
        })

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            provider.get_country_info("Poland")

            # Verify JSON mode was used
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["response_format"] == {"type": "json_object"}

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_get_country_info_raises_on_invalid_json(self) -> None:
        """Test get_country_info raises on invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not valid JSON at all"

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_country_info("Poland")

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_get_country_info_raises_on_empty_json(self) -> None:
        """Test get_country_info raises on empty JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "{}"

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            with pytest.raises(ValueError, match="Empty JSON response"):
                provider.get_country_info("Poland")


class TestGetCitiesInfo:
    """Tests for get_cities_info method."""

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_get_cities_info_parses_json_response(self) -> None:
        """Test get_cities_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "cities": [
                {
                    "name": "Warsaw",
                    "is_capital": True,
                    "description": "Capital of Poland",
                    "interesting_fact": "Largest city",
                    "area_sq_mile": 202.0,
                    "area_sq_km": 523.0,
                    "population": 1800000,
                    "sci_score": None,
                    "sci_rank": None,
                    "numbeo_si": 65.0,
                    "numbeo_ci": 35.0,
                    "airport_code": "WAW",
                }
            ]
        })

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            cities = provider.get_cities_info("Poland")

            assert len(cities) == 1
            assert cities[0].name == "Warsaw"
            assert cities[0].is_capital is True
            assert cities[0].population == 1800000

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_get_cities_info_handles_multiple_cities(self) -> None:
        """Test get_cities_info handles multiple cities."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "cities": [
                {
                    "name": "Warsaw",
                    "is_capital": True,
                    "description": "Capital",
                    "interesting_fact": "Fact 1",
                    "area_sq_mile": 202.0,
                    "area_sq_km": 523.0,
                    "population": 1800000,
                    "sci_score": None,
                    "sci_rank": None,
                    "numbeo_si": None,
                    "numbeo_ci": None,
                    "airport_code": "WAW",
                },
                {
                    "name": "Krakow",
                    "is_capital": False,
                    "description": "Historic city",
                    "interesting_fact": "Fact 2",
                    "area_sq_mile": 126.0,
                    "area_sq_km": 327.0,
                    "population": 800000,
                    "sci_score": None,
                    "sci_rank": None,
                    "numbeo_si": None,
                    "numbeo_ci": None,
                    "airport_code": "KRK",
                },
            ]
        })

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            cities = provider.get_cities_info("Poland")

            assert len(cities) == 2
            assert cities[0].name == "Warsaw"
            assert cities[1].name == "Krakow"

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    def test_get_cities_info_raises_on_invalid_json(self) -> None:
        """Test get_cities_info raises on invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not valid JSON"

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_cities_info("Poland")


class TestRetryLogic:
    """Tests for retry logic in provider methods."""

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    @patch("process_structured_output.providers.deepseek_provider.time.sleep")
    def test_get_country_info_with_retry_retries_on_failure(
        self, mock_sleep: MagicMock
    ) -> None:
        """Test retry logic retries on transient failures."""
        valid_response = MagicMock()
        valid_response.choices = [MagicMock()]
        valid_response.choices[0].message.content = json.dumps({
            "description": "Test",
            "interesting_fact": "Fact",
            "area_sq_mile": 100.0,
            "area_sq_km": 259.0,
            "population": 1000000,
            "ppp": 1000.0,
            "life_expectancy": 75.0,
            "travel_risk_level": "Low",
            "global_peace_index_score": 1.5,
            "global_peace_index_rank": 20,
            "happiness_index_score": 6.5,
            "happiness_index_rank": 25,
            "gdp": 100000000.0,
            "gdp_growth_rate": 2.0,
            "inflation_rate": 2.0,
            "unemployment_rate": 5.0,
            "govt_debt": 50.0,
            "credit_rating": "AA",
            "poverty_rate": 10.0,
            "gini_coefficient": 30.0,
            "military_spending": 2.0,
        })

        # First call fails with empty content, second succeeds
        fail_response = MagicMock()
        fail_response.choices = [MagicMock()]
        fail_response.choices[0].message.content = "{}"

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                fail_response,
                valid_response,
            ]
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            info = provider.get_country_info_with_retry("Poland")

            assert info.description == "Test"
            assert mock_sleep.call_count == 1
            mock_sleep.assert_called_with(RETRY_DELAY)

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    @patch("process_structured_output.providers.deepseek_provider.time.sleep")
    def test_retry_fails_after_max_retries(self, mock_sleep: MagicMock) -> None:
        """Test retry gives up after max retries."""
        fail_response = MagicMock()
        fail_response.choices = [MagicMock()]
        fail_response.choices[0].message.content = "{}"

        with patch(
            "process_structured_output.providers.deepseek_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = fail_response
            mock_openai.return_value = mock_client

            provider = DeepSeekProvider()
            with pytest.raises(ValueError, match=f"Failed after {MAX_RETRIES}"):
                provider.get_country_info_with_retry("Poland")


class TestConstants:
    """Tests for module constants."""

    def test_max_retries_value(self) -> None:
        """Test MAX_RETRIES has expected value."""
        assert MAX_RETRIES == 3

    def test_retry_delay_value(self) -> None:
        """Test RETRY_DELAY has expected value."""
        assert RETRY_DELAY == 1.0

    def test_rate_limit_delay_value(self) -> None:
        """Test RATE_LIMIT_DELAY has expected value."""
        assert RATE_LIMIT_DELAY == 10.0
