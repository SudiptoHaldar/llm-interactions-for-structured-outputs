"""Tests for AI21 batch country processing CLI."""

from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.cli_all_countries_ai21 import main


class TestBatchCLI:
    """Tests for all-countries-ai21 CLI."""

    @patch("process_structured_output.cli_all_countries_ai21.get_countries_by_llm")
    @patch("process_structured_output.cli_all_countries_ai21.process_country")
    def test_dry_run_lists_countries(
        self,
        mock_process: MagicMock,
        mock_get_countries: MagicMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test dry run mode shows countries without processing."""
        mock_get_countries.return_value = ["Nigeria", "Argentina"]

        with patch("sys.argv", ["cli", "--dry-run"]):
            result = main()

        assert result == 0
        mock_process.assert_not_called()
        output = capsys.readouterr().out
        assert "Nigeria" in output
        assert "Argentina" in output
        assert "DRY RUN" in output

    @patch("process_structured_output.cli_all_countries_ai21.get_countries_by_llm")
    @patch("process_structured_output.cli_all_countries_ai21.process_country")
    def test_processes_all_countries(
        self,
        mock_process: MagicMock,
        mock_get_countries: MagicMock,
    ) -> None:
        """Test all countries are processed."""
        mock_get_countries.return_value = ["Nigeria", "Argentina"]
        mock_process.return_value = {"ai_model_id": 1, "country_id": 1}

        with patch("sys.argv", ["cli"]):
            result = main()

        assert result == 0
        assert mock_process.call_count == 2

    @patch("process_structured_output.cli_all_countries_ai21.get_countries_by_llm")
    @patch("process_structured_output.cli_all_countries_ai21.process_country")
    def test_returns_error_on_any_failure(
        self,
        mock_process: MagicMock,
        mock_get_countries: MagicMock,
    ) -> None:
        """Test returns 1 if any country fails."""
        mock_get_countries.return_value = ["Nigeria", "Argentina"]
        mock_process.side_effect = [
            {"ai_model_id": 1, "country_id": 1},  # Nigeria succeeds
            ValueError("API error"),  # Argentina fails
        ]

        with patch("sys.argv", ["cli"]):
            result = main()

        assert result == 1

    @patch("process_structured_output.cli_all_countries_ai21.get_countries_by_llm")
    @patch("process_structured_output.cli_all_countries_ai21.process_country")
    def test_skip_cities_passed_through(
        self,
        mock_process: MagicMock,
        mock_get_countries: MagicMock,
    ) -> None:
        """Test --skip-cities flag is passed to process_country."""
        mock_get_countries.return_value = ["Nigeria"]
        mock_process.return_value = {"ai_model_id": 1, "country_id": 1}

        with patch("sys.argv", ["cli", "--skip-cities"]):
            main()

        mock_process.assert_called_once_with(
            country_name="Nigeria",
            provider="ai21",
            skip_cities=True,
        )
