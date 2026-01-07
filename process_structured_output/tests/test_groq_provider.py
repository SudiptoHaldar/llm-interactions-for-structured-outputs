"""Tests for Groq provider."""

import json
from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.providers.groq_provider import (
    MAX_RETRIES,
    RETRY_DELAY,
    GroqProvider,
)


class TestGroqProviderInit:
    """Tests for GroqProvider initialization."""

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_init_with_env_var(self) -> None:
        """Test provider initializes with env var."""
        with patch("process_structured_output.providers.groq_provider.Groq"):
            provider = GroqProvider()
            assert provider.api_key == "test-key"
            assert provider.model == "meta-llama/llama-4-scout-17b-16e-instruct"

    def test_init_with_explicit_key(self) -> None:
        """Test provider initializes with explicit key."""
        with patch("process_structured_output.providers.groq_provider.Groq"):
            provider = GroqProvider(api_key="explicit-key")
            assert provider.api_key == "explicit-key"

    @patch("process_structured_output.providers.groq_provider.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_raises_without_key(self, mock_load_dotenv: MagicMock) -> None:
        """Test provider raises error without API key."""
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            GroqProvider()


class TestGetModelIdentity:
    """Tests for get_model_identity method."""

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_get_model_identity_returns_hardcoded_values(self) -> None:
        """Test get_model_identity returns hardcoded provider and model name."""
        with patch("process_structured_output.providers.groq_provider.Groq"):
            provider = GroqProvider()
            identity = provider.get_model_identity()

            # Hardcoded values - no API call made
            assert identity.model_provider == "Groq"
            assert identity.model_name == "meta-llama/llama-4-scout-17b-16e-instruct"


class TestGetContinentInfo:
    """Tests for get_continent_info method."""

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_get_continent_info_parses_json(self) -> None:
        """Test get_continent_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "description": "Test continent",
            "area_sq_mile": 1000000,
            "area_sq_km": 2590000,
            "population": 500000000,
            "num_country": 50,
        })

        with patch(
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            info = provider.get_continent_info("TestContinent")

            assert info.description == "Test continent"
            assert info.population == 500000000

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_get_continent_info_raises_on_invalid_json(self) -> None:
        """Test get_continent_info raises on invalid JSON."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not json"

        with patch(
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_continent_info("TestContinent")


class TestGetCountryInfo:
    """Tests for get_country_info method."""

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
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
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            info = provider.get_country_info("Ghana")

            assert info.description == "Test country"
            assert info.population == 220000000
            assert info.gdp == 450000000000.0

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
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
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            provider.get_country_info("Estonia")

            # Verify JSON mode was used
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["response_format"] == {"type": "json_object"}

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_get_country_info_raises_on_invalid_json(self) -> None:
        """Test get_country_info raises on invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not valid JSON at all"

        with patch(
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_country_info("Ghana")

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_get_country_info_raises_on_empty_json(self) -> None:
        """Test get_country_info raises on empty JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "{}"

        with patch(
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            with pytest.raises(ValueError, match="Empty JSON response"):
                provider.get_country_info("Ghana")


class TestGetCitiesInfo:
    """Tests for get_cities_info method."""

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_get_cities_info_parses_json_response(self) -> None:
        """Test get_cities_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "cities": [
                {
                    "name": "Accra",
                    "is_capital": True,
                    "description": "Capital of Ghana",
                    "interesting_fact": "Largest city",
                    "area_sq_mile": 225.0,
                    "area_sq_km": 583.0,
                    "population": 2500000,
                    "sci_score": None,
                    "sci_rank": None,
                    "numbeo_si": 45.0,
                    "numbeo_ci": 55.0,
                    "airport_code": "ACC",
                }
            ]
        })

        with patch(
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            cities = provider.get_cities_info("Ghana")

            assert len(cities) == 1
            assert cities[0].name == "Accra"
            assert cities[0].is_capital is True
            assert cities[0].population == 2500000

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_get_cities_info_handles_multiple_cities(self) -> None:
        """Test get_cities_info handles multiple cities."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "cities": [
                {
                    "name": "London",
                    "is_capital": True,
                    "description": "Capital",
                    "interesting_fact": "Fact 1",
                    "area_sq_mile": 607.0,
                    "area_sq_km": 1572.0,
                    "population": 8900000,
                    "sci_score": 75.0,
                    "sci_rank": 14,
                    "numbeo_si": None,
                    "numbeo_ci": None,
                    "airport_code": "LHR",
                },
                {
                    "name": "Birmingham",
                    "is_capital": False,
                    "description": "Second city",
                    "interesting_fact": "Fact 2",
                    "area_sq_mile": 103.0,
                    "area_sq_km": 267.0,
                    "population": 1140000,
                    "sci_score": None,
                    "sci_rank": None,
                    "numbeo_si": None,
                    "numbeo_ci": None,
                    "airport_code": "BHX",
                },
            ]
        })

        with patch(
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            cities = provider.get_cities_info("United Kingdom")

            assert len(cities) == 2
            assert cities[0].name == "London"
            assert cities[1].name == "Birmingham"

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_get_cities_info_raises_on_invalid_json(self) -> None:
        """Test get_cities_info raises on invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not valid JSON"

        with patch(
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_cities_info("Ghana")


class TestRetryLogic:
    """Tests for retry logic in provider methods."""

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("process_structured_output.providers.groq_provider.time.sleep")
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
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                fail_response,
                valid_response,
            ]
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            info = provider.get_country_info_with_retry("Estonia")

            assert info.description == "Test"
            assert mock_sleep.call_count == 1
            mock_sleep.assert_called_with(RETRY_DELAY)

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("process_structured_output.providers.groq_provider.time.sleep")
    def test_retry_fails_after_max_retries(self, mock_sleep: MagicMock) -> None:
        """Test retry gives up after max retries."""
        fail_response = MagicMock()
        fail_response.choices = [MagicMock()]
        fail_response.choices[0].message.content = "{}"

        with patch(
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = fail_response
            mock_groq.return_value = mock_client

            provider = GroqProvider()
            with pytest.raises(ValueError, match=f"Failed after {MAX_RETRIES}"):
                provider.get_country_info_with_retry("Estonia")

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("process_structured_output.providers.groq_provider.time.sleep")
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
            "process_structured_output.providers.groq_provider.Groq"
        ) as mock_groq:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = [
                fail_response,
                valid_response,
            ]
            mock_groq.return_value = mock_client

            provider = GroqProvider()
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
