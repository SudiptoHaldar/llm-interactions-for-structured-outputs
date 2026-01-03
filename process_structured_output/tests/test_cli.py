"""Tests for CLI module."""

from unittest.mock import MagicMock, patch

from process_structured_output.cli import VALID_CONTINENTS, main


class TestValidContinents:
    """Tests for continent validation."""

    def test_valid_continents_list(self) -> None:
        """Test valid continents list contains expected values."""
        assert "Africa" in VALID_CONTINENTS
        assert "Asia" in VALID_CONTINENTS
        assert "Europe" in VALID_CONTINENTS
        assert "North America" in VALID_CONTINENTS
        assert len(VALID_CONTINENTS) == 7

    def test_all_seven_continents(self) -> None:
        """Test all seven continents are included."""
        expected = [
            "Africa",
            "Antarctica",
            "Asia",
            "Europe",
            "North America",
            "Oceania",
            "South America",
        ]
        for continent in expected:
            assert continent in VALID_CONTINENTS


class TestCLI:
    """Tests for CLI main function."""

    def test_invalid_continent_returns_error(self) -> None:
        """Test invalid continent name returns error code."""
        with patch("sys.argv", ["cli.py", "InvalidContinent"]):
            result = main()
            assert result == 1

    def test_atlantis_fails_validation(self) -> None:
        """Test fictional continent fails validation."""
        with patch("sys.argv", ["cli.py", "Atlantis"]):
            result = main()
            assert result == 1

    @patch("process_structured_output.cli.OpenAIProvider")
    @patch("process_structured_output.cli.upsert_ai_model")
    @patch("process_structured_output.cli.upsert_continent")
    def test_successful_execution(
        self,
        mock_upsert_continent: MagicMock,
        mock_upsert_model: MagicMock,
        mock_provider_class: MagicMock,
    ) -> None:
        """Test successful CLI execution."""
        from process_structured_output.models.continent import (
            ContinentInfo,
            ModelIdentity,
        )

        mock_provider = MagicMock()
        mock_provider.get_model_identity.return_value = ModelIdentity(
            model_provider="OpenAI", model_name="gpt-4o"
        )
        mock_provider.get_continent_info.return_value = ContinentInfo(
            description="Test continent description for testing purposes",
            area_sq_mile=1000.0,
            area_sq_km=2590.0,
            population=1000000,
            num_country=5,
        )
        mock_provider_class.return_value = mock_provider
        mock_upsert_model.return_value = 1
        mock_upsert_continent.return_value = 1

        with patch("sys.argv", ["cli.py", "Africa"]):
            result = main()
            assert result == 0

        mock_upsert_model.assert_called_once()
        mock_upsert_continent.assert_called_once()

    @patch("process_structured_output.cli.OpenAIProvider")
    def test_api_error_returns_error_code(
        self,
        mock_provider_class: MagicMock,
    ) -> None:
        """Test API error returns error code."""
        mock_provider = MagicMock()
        mock_provider.get_model_identity.side_effect = ValueError("API error")
        mock_provider_class.return_value = mock_provider

        with patch("sys.argv", ["cli.py", "Africa"]):
            result = main()
            assert result == 1

    @patch("process_structured_output.cli.GoogleProvider")
    @patch("process_structured_output.cli.upsert_ai_model")
    @patch("process_structured_output.cli.upsert_continent")
    def test_google_provider_execution(
        self,
        mock_upsert_continent: MagicMock,
        mock_upsert_model: MagicMock,
        mock_provider_class: MagicMock,
    ) -> None:
        """Test CLI execution with Google provider."""
        from process_structured_output.models.continent import (
            ContinentInfo,
            ModelIdentity,
        )

        mock_provider = MagicMock()
        mock_provider.get_model_identity.return_value = ModelIdentity(
            model_provider="Google", model_name="gemini-2.5-flash"
        )
        mock_provider.get_continent_info.return_value = ContinentInfo(
            description="Test continent description for testing purposes",
            area_sq_mile=1000.0,
            area_sq_km=2590.0,
            population=1000000,
            num_country=5,
        )
        mock_provider_class.return_value = mock_provider
        mock_upsert_model.return_value = 1
        mock_upsert_continent.return_value = 1

        with patch("sys.argv", ["cli.py", "Africa", "--provider", "google"]):
            result = main()
            assert result == 0

        mock_provider_class.assert_called_once()
