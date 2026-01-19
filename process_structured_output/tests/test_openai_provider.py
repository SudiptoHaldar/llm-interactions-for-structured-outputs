"""Tests for OpenAI provider."""

import json
from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.providers.openai_provider import (
    MAX_RETRIES,
    RETRY_DELAY,
    OpenAIProvider,
)


class TestOpenAIProvider:
    """Tests for OpenAIProvider initialization."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_init_with_env_var(self) -> None:
        """Test provider initializes with env var."""
        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ):
            provider = OpenAIProvider()
            assert provider.api_key == "test-key"

    def test_init_with_explicit_key(self) -> None:
        """Test provider initializes with explicit key."""
        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ):
            provider = OpenAIProvider(api_key="explicit-key")
            assert provider.api_key == "explicit-key"

    @patch("process_structured_output.providers.openai_provider.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_raises_without_key(self, mock_load_dotenv: MagicMock) -> None:
        """Test provider raises error without API key."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            OpenAIProvider()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_model_identity_returns_hardcoded_values(self) -> None:
        """Test get_model_identity returns hardcoded provider and model name."""
        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ):
            provider = OpenAIProvider()
            identity = provider.get_model_identity()

            # Hardcoded values - no API call made
            assert identity.model_provider == "OpenAI"
            assert identity.model_name == "gpt-4o"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_continent_info_parses_json(self) -> None:
        """Test get_continent_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=(
                        '{"description": "Test", "area_sq_mile": 1000.0, '
                        '"area_sq_km": 2590.0, "population": 1000000, '
                        '"num_country": 5}'
                    )
                )
            )
        ]

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            info = provider.get_continent_info("TestContinent")

            assert info.description == "Test"
            assert info.area_sq_mile == 1000.0
            assert info.population == 1000000

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_continent_info_raises_on_invalid_json(self) -> None:
        """Test get_continent_info raises on invalid JSON."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="not json"))
        ]

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_continent_info("TestContinent")


class TestGetCountryInfo:
    """Tests for get_country_info method."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_country_info_parses_json_response(self) -> None:
        """Test get_country_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "description": "Test country",
            "interesting_fact": "A fun fact",
            "area_sq_mile": 356669.0,
            "area_sq_km": 923768.0,
            "population": 67000000,
            "ppp": 45000.0,
            "life_expectancy": 82.0,
            "travel_risk_level": "Level 1",
            "global_peace_index_score": 1.9,
            "global_peace_index_rank": 65,
            "happiness_index_score": 6.5,
            "happiness_index_rank": 21,
            "gdp": 2800000000000.0,
            "gdp_growth_rate": 2.5,
            "inflation_rate": 5.0,
            "unemployment_rate": 7.0,
            "govt_debt": 110.0,
            "credit_rating": "AA",
            "poverty_rate": 15.0,
            "gini_coefficient": 32.0,
            "military_spending": 2.1,
            "gdp_per_capita": 41800.0,
        })

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            info = provider.get_country_info("France")

            assert info.description == "Test country"
            assert info.population == 67000000
            assert info.gdp == 2800000000000.0

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
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
            "gdp_per_capita": 100.0,
        })

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            provider.get_country_info("Morocco")

            # Verify JSON mode was used
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["response_format"] == {"type": "json_object"}

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_country_info_raises_on_invalid_json(self) -> None:
        """Test get_country_info raises on invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not valid JSON at all"

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_country_info("France")

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_country_info_raises_on_empty_json(self) -> None:
        """Test get_country_info raises on empty JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "{}"

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            with pytest.raises(ValueError, match="Empty JSON response"):
                provider.get_country_info("France")


class TestGetCitiesInfo:
    """Tests for get_cities_info method."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_cities_info_parses_json_response(self) -> None:
        """Test get_cities_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "cities": [
                {
                    "name": "Paris",
                    "is_capital": True,
                    "description": "Capital of France",
                    "interesting_fact": "City of lights",
                    "area_sq_mile": 40.0,
                    "area_sq_km": 105.0,
                    "population": 2200000,
                    "sci_score": 82.0,
                    "sci_rank": 5,
                    "numbeo_si": 48.0,
                    "numbeo_ci": 52.0,
                    "airport_code": "CDG",
                }
            ]
        })

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            cities = provider.get_cities_info("France")

            assert len(cities) == 1
            assert cities[0].name == "Paris"
            assert cities[0].is_capital is True
            assert cities[0].population == 2200000

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_cities_info_handles_multiple_cities(self) -> None:
        """Test get_cities_info handles multiple cities."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "cities": [
                {
                    "name": "Paris",
                    "is_capital": True,
                    "description": "Capital",
                    "interesting_fact": "Fact 1",
                    "area_sq_mile": 40.0,
                    "area_sq_km": 105.0,
                    "population": 2200000,
                    "sci_score": 82.0,
                    "sci_rank": 5,
                    "numbeo_si": None,
                    "numbeo_ci": None,
                    "airport_code": "CDG",
                },
                {
                    "name": "Marseille",
                    "is_capital": False,
                    "description": "Second city",
                    "interesting_fact": "Fact 2",
                    "area_sq_mile": 92.0,
                    "area_sq_km": 240.0,
                    "population": 870000,
                    "sci_score": None,
                    "sci_rank": None,
                    "numbeo_si": None,
                    "numbeo_ci": None,
                    "airport_code": "MRS",
                },
            ]
        })

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            cities = provider.get_cities_info("France")

            assert len(cities) == 2
            assert cities[0].name == "Paris"
            assert cities[1].name == "Marseille"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_cities_info_raises_on_invalid_json(self) -> None:
        """Test get_cities_info raises on invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not valid JSON"

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_cities_info("France")


class TestRetryLogic:
    """Tests for retry logic in provider methods."""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("process_structured_output.providers.openai_provider.time.sleep")
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
            "gdp_per_capita": 100.0,
        })

        # First call fails with empty content, second succeeds
        fail_response = MagicMock()
        fail_response.choices = [MagicMock()]
        fail_response.choices[0].message.content = "{}"

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                fail_response,
                valid_response,
            ]
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            info = provider.get_country_info_with_retry("Morocco")

            assert info.description == "Test"
            assert mock_sleep.call_count == 1
            mock_sleep.assert_called_with(RETRY_DELAY)

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("process_structured_output.providers.openai_provider.time.sleep")
    def test_retry_fails_after_max_retries(self, mock_sleep: MagicMock) -> None:
        """Test retry gives up after max retries."""
        fail_response = MagicMock()
        fail_response.choices = [MagicMock()]
        fail_response.choices[0].message.content = "{}"

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = fail_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            with pytest.raises(ValueError, match=f"Failed after {MAX_RETRIES}"):
                provider.get_country_info_with_retry("Morocco")

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("process_structured_output.providers.openai_provider.time.sleep")
    def test_get_cities_info_with_retry_retries_on_failure(
        self, mock_sleep: MagicMock
    ) -> None:
        """Test cities retry logic retries on transient failures."""
        valid_response = MagicMock()
        valid_response.choices = [MagicMock()]
        valid_response.choices[0].message.content = json.dumps({
            "cities": [{
                "name": "Test City",
                "is_capital": True,
                "description": "Test",
                "interesting_fact": "Fact",
                "area_sq_mile": 100.0,
                "area_sq_km": 259.0,
                "population": 1000000,
                "sci_score": None,
                "sci_rank": None,
                "numbeo_si": None,
                "numbeo_ci": None,
                "airport_code": "TST",
            }]
        })

        # First call fails, second succeeds
        fail_response = MagicMock()
        fail_response.choices = [MagicMock()]
        fail_response.choices[0].message.content = "invalid json"

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                fail_response,
                valid_response,
            ]
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            cities = provider.get_cities_info_with_retry("Test")

            assert len(cities) == 1
            assert cities[0].name == "Test City"
            assert mock_sleep.call_count == 1


class TestConstants:
    """Tests for module constants."""

    def test_max_retries_value(self) -> None:
        """Test MAX_RETRIES has expected value."""
        assert MAX_RETRIES == 3

    def test_retry_delay_value(self) -> None:
        """Test RETRY_DELAY has expected value."""
        assert RETRY_DELAY == 1.0
