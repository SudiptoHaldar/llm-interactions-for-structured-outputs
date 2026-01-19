"""Tests for AI21 provider."""

from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.providers.ai21_provider import AI21Provider


class TestAI21Provider:
    """Tests for AI21Provider."""

    @patch.dict("os.environ", {"AI21_API_KEY": "test-key"})
    def test_init_with_env_var(self) -> None:
        """Test provider initializes with env var."""
        with patch(
            "process_structured_output.providers.ai21_provider.AI21Client"
        ):
            provider = AI21Provider()
            assert provider.api_key == "test-key"

    def test_init_with_explicit_key(self) -> None:
        """Test provider initializes with explicit key."""
        with patch(
            "process_structured_output.providers.ai21_provider.AI21Client"
        ):
            provider = AI21Provider(api_key="explicit-key")
            assert provider.api_key == "explicit-key"

    @patch("process_structured_output.providers.ai21_provider.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_raises_without_key(self, mock_load_dotenv: MagicMock) -> None:
        """Test provider raises error without API key."""
        with pytest.raises(ValueError, match="AI21_API_KEY"):
            AI21Provider()

    @patch.dict("os.environ", {"AI21_API_KEY": "test-key"})
    def test_get_model_identity_returns_hardcoded_values(self) -> None:
        """Test get_model_identity returns hardcoded provider and model name."""
        with patch(
            "process_structured_output.providers.ai21_provider.AI21Client"
        ):
            provider = AI21Provider()
            identity = provider.get_model_identity()

            # Hardcoded values - no API call made
            assert identity.model_provider == "AI21"
            assert identity.model_name == "jamba-mini"

    @patch.dict("os.environ", {"AI21_API_KEY": "test-key"})
    def test_get_country_info_parses_json(self) -> None:
        """Test get_country_info parses JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=(
                        '{"description": "Test country", '
                        '"interesting_fact": "A fun fact", '
                        '"area_sq_mile": 356669.0, '
                        '"area_sq_km": 923768.0, '
                        '"population": 220000000, '
                        '"ppp": 5500.0, '
                        '"life_expectancy": 55.0, '
                        '"travel_risk_level": "Level 3", '
                        '"global_peace_index_score": 2.7, '
                        '"global_peace_index_rank": 144, '
                        '"happiness_index_score": 4.5, '
                        '"happiness_index_rank": 99, '
                        '"gdp": 450000000000.0, '
                        '"gdp_growth_rate": 3.5, '
                        '"inflation_rate": 18.0, '
                        '"unemployment_rate": 5.0, '
                        '"govt_debt": 38.0, '
                        '"credit_rating": "B-", '
                        '"poverty_rate": 40.0, '
                        '"gini_coefficient": 35.0, '
                        '"military_spending": 0.6, "gdp_per_capita": 2045.0}'
                    )
                )
            )
        ]

        with patch(
            "process_structured_output.providers.ai21_provider.AI21Client"
        ) as mock_ai21:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_ai21.return_value = mock_client

            provider = AI21Provider()
            info = provider.get_country_info("Nigeria")

            assert info.description == "Test country"
            assert info.area_sq_mile == 356669.0
            assert info.population == 220000000
            assert info.gdp == 450000000000.0

    @patch.dict("os.environ", {"AI21_API_KEY": "test-key"})
    def test_get_country_info_raises_on_invalid_json(self) -> None:
        """Test get_country_info raises on invalid JSON."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="not json"))
        ]

        with patch(
            "process_structured_output.providers.ai21_provider.AI21Client"
        ) as mock_ai21:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_ai21.return_value = mock_client

            provider = AI21Provider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_country_info("Nigeria")

    @patch.dict("os.environ", {"AI21_API_KEY": "test-key"})
    def test_get_cities_info_parses_json(self) -> None:
        """Test get_cities_info parses JSON response with cities array."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=(
                        '{"cities": ['
                        '{"name": "Lagos", "is_capital": false, '
                        '"description": "Economic hub", '
                        '"interesting_fact": "Most populous city", '
                        '"area_sq_mile": 452.0, '
                        '"area_sq_km": 1171.0, '
                        '"population": 15000000, '
                        '"sci_score": null, '
                        '"sci_rank": null, '
                        '"numbeo_si": 35.0, '
                        '"numbeo_ci": 65.0, '
                        '"airport_code": "LOS"}'
                        ']}'
                    )
                )
            )
        ]

        with patch(
            "process_structured_output.providers.ai21_provider.AI21Client"
        ) as mock_ai21:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_ai21.return_value = mock_client

            provider = AI21Provider()
            cities = provider.get_cities_info("Nigeria")

            assert len(cities) == 1
            assert cities[0].name == "Lagos"
            assert cities[0].is_capital is False
            assert cities[0].population == 15000000
            assert cities[0].airport_code == "LOS"

    @patch.dict("os.environ", {"AI21_API_KEY": "test-key"})
    def test_get_cities_info_raises_on_invalid_json(self) -> None:
        """Test get_cities_info raises on invalid JSON."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="not json"))
        ]

        with patch(
            "process_structured_output.providers.ai21_provider.AI21Client"
        ) as mock_ai21:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_ai21.return_value = mock_client

            provider = AI21Provider()
            with pytest.raises(ValueError, match="Failed to parse"):
                provider.get_cities_info("Nigeria")
