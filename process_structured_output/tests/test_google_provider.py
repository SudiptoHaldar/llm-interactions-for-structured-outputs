"""Tests for Google Gemini provider."""

import json
from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.providers.google_provider import GoogleProvider


class TestGoogleProvider:
    """Tests for GoogleProvider."""

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    def test_init_with_env_var(self) -> None:
        """Test provider initializes with env var."""
        with patch(
            "process_structured_output.providers.google_provider.genai"
        ):
            provider = GoogleProvider()
            assert provider.api_key == "test-key"

    def test_init_with_explicit_key(self) -> None:
        """Test provider initializes with explicit key."""
        with patch(
            "process_structured_output.providers.google_provider.genai"
        ):
            provider = GoogleProvider(api_key="explicit-key")
            assert provider.api_key == "explicit-key"

    @patch("process_structured_output.providers.google_provider.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_raises_without_key(self, mock_load_dotenv: MagicMock) -> None:
        """Test provider raises error without API key."""
        with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
            GoogleProvider()

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    def test_get_model_identity_returns_hardcoded_values(self) -> None:
        """Test get_model_identity returns hardcoded provider and model name."""
        with patch(
            "process_structured_output.providers.google_provider.genai"
        ):
            provider = GoogleProvider()
            identity = provider.get_model_identity()

            # Hardcoded values - no API call made
            assert identity.model_provider == "Google"
            assert identity.model_name == "gemini-2.5-flash"

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    def test_get_continent_info_parses_json(self) -> None:
        """Test get_continent_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.text = (
            '{"description": "Test", "area_sq_mile": 1000.0, '
            '"area_sq_km": 2590.0, "population": 1000000, '
            '"num_country": 5}'
        )

        with patch(
            "process_structured_output.providers.google_provider.genai"
        ) as mock_genai:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            provider = GoogleProvider()
            info = provider.get_continent_info("TestContinent")

            assert info.description == "Test"
            assert info.area_sq_mile == 1000.0
            assert info.population == 1000000

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    def test_get_continent_info_raises_on_invalid_json(self) -> None:
        """Test get_continent_info raises on invalid JSON."""
        mock_response = MagicMock()
        mock_response.text = "not json"

        with patch(
            "process_structured_output.providers.google_provider.genai"
        ) as mock_genai:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            provider = GoogleProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_continent_info("TestContinent")


class TestGetCountryInfo:
    """Tests for get_country_info method."""

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    def test_get_country_info_parses_json(self) -> None:
        """Test get_country_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "description": "Test country",
            "interesting_fact": "Test fact",
            "area_sq_mile": 100000,
            "area_sq_km": 259000,
            "population": 50000000,
            "ppp": 1500000000000,
            "life_expectancy": 75.5,
            "travel_risk_level": "Level 1",
            "global_peace_index_score": 1.5,
            "global_peace_index_rank": 20,
            "happiness_index_score": 6.5,
            "happiness_index_rank": 25,
            "gdp": 500000000000,
            "gdp_growth_rate": 3.5,
            "inflation_rate": 2.0,
            "unemployment_rate": 5.0,
            "govt_debt": 60.0,
            "credit_rating": "AA",
            "poverty_rate": 10.0,
            "gini_coefficient": 35.0,
            "military_spending": 2.0
        })

        with patch(
            "process_structured_output.providers.google_provider.genai"
        ) as mock_genai:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            provider = GoogleProvider()
            info = provider.get_country_info("TestCountry")

            assert info.description == "Test country"
            assert info.population == 50000000

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    def test_get_country_info_raises_on_invalid_json(self) -> None:
        """Test get_country_info raises on invalid JSON."""
        mock_response = MagicMock()
        mock_response.text = "not json"

        with patch(
            "process_structured_output.providers.google_provider.genai"
        ) as mock_genai:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            provider = GoogleProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_country_info("TestCountry")


class TestGetCitiesInfo:
    """Tests for get_cities_info method."""

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    def test_get_cities_info_parses_json(self) -> None:
        """Test get_cities_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "cities": [{
                "name": "Test City",
                "is_capital": True,
                "description": "Capital city",
                "interesting_fact": "Test fact",
                "area_sq_mile": 500,
                "area_sq_km": 1295,
                "population": 5000000,
                "sci_score": None,
                "sci_rank": None,
                "numbeo_si": None,
                "numbeo_ci": None,
                "airport_code": "TST"
            }]
        })

        with patch(
            "process_structured_output.providers.google_provider.genai"
        ) as mock_genai:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            provider = GoogleProvider()
            cities = provider.get_cities_info("TestCountry")

            assert len(cities) == 1
            assert cities[0].name == "Test City"
            assert cities[0].is_capital is True

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    def test_get_cities_info_raises_on_invalid_json(self) -> None:
        """Test get_cities_info raises on invalid JSON."""
        mock_response = MagicMock()
        mock_response.text = "not json"

        with patch(
            "process_structured_output.providers.google_provider.genai"
        ) as mock_genai:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            provider = GoogleProvider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_cities_info("TestCountry")


class TestRetryLogic:
    """Tests for retry logic."""

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    @patch("process_structured_output.providers.google_provider.time.sleep")
    def test_get_country_info_with_retry_retries_on_failure(
        self, mock_sleep: MagicMock
    ) -> None:
        """Test retry logic retries on failure."""
        mock_response_fail = MagicMock()
        mock_response_fail.text = "invalid"

        mock_response_success = MagicMock()
        mock_response_success.text = json.dumps({
            "description": "Test", "interesting_fact": "Fact",
            "area_sq_mile": 100, "area_sq_km": 259, "population": 1000,
            "ppp": 1000, "life_expectancy": 75, "travel_risk_level": "Low",
            "global_peace_index_score": 1.5, "global_peace_index_rank": 1,
            "happiness_index_score": 6.5, "happiness_index_rank": 1,
            "gdp": 1000, "gdp_growth_rate": 3.5, "inflation_rate": 2.0,
            "unemployment_rate": 5.0, "govt_debt": 60.0, "credit_rating": "AA",
            "poverty_rate": 10.0, "gini_coefficient": 35.0, "military_spending": 2.0
        })

        with patch(
            "process_structured_output.providers.google_provider.genai"
        ) as mock_genai:
            mock_client = MagicMock()
            mock_client.models.generate_content.side_effect = [
                mock_response_fail,
                mock_response_success
            ]
            mock_genai.Client.return_value = mock_client

            provider = GoogleProvider()
            result = provider.get_country_info_with_retry("Test")

            assert result.description == "Test"
            assert mock_client.models.generate_content.call_count == 2

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    @patch("process_structured_output.providers.google_provider.time.sleep")
    def test_retry_fails_after_max_retries(
        self, mock_sleep: MagicMock
    ) -> None:
        """Test retry fails after max attempts."""
        mock_response = MagicMock()
        mock_response.text = "invalid json"

        with patch(
            "process_structured_output.providers.google_provider.genai"
        ) as mock_genai:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            provider = GoogleProvider()
            with pytest.raises(ValueError, match="Failed after"):
                provider.get_country_info_with_retry("Test")
