"""Tests for OpenAI provider."""

from unittest.mock import MagicMock, patch

import pytest

from process_structured_output.providers.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""

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
    def test_get_model_identity_parses_response(self) -> None:
        """Test get_model_identity parses response correctly."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Model Provider: OpenAI | Model Name: gpt-4o"
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
            identity = provider.get_model_identity()

            assert identity.model_provider == "OpenAI"
            assert identity.model_name == "gpt-4o"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_get_model_identity_raises_on_invalid_format(self) -> None:
        """Test get_model_identity raises on invalid response format."""
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="I am ChatGPT")
            )
        ]

        with patch(
            "process_structured_output.providers.openai_provider.OpenAI"
        ) as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            provider = OpenAIProvider()
            with pytest.raises(ValueError, match="Could not parse"):
                provider.get_model_identity()

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
