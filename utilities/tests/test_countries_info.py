"""Tests for countries_info module."""

import pytest

from utilities.countries_info import (
    CountryInfo,
    get_all_countries,
    get_continents,
    get_countries_by_continent,
    get_countries_by_llm,
    get_country_info,
    get_llms,
    reload_data,
)


class TestGetContinents:
    """Tests for get_continents function."""

    def test_returns_list(self) -> None:
        """Test that get_continents returns a list."""
        result = get_continents()
        assert isinstance(result, list)

    def test_contains_africa(self) -> None:
        """Test that Africa is in the list."""
        result = get_continents()
        assert "Africa" in result

    def test_contains_key_continents(self) -> None:
        """Test that key continents are present."""
        result = get_continents()
        # At least these should be present based on CSV
        for continent in ["Africa", "Asia", "Europe"]:
            assert continent in result

    def test_is_sorted(self) -> None:
        """Test that continents are sorted alphabetically."""
        result = get_continents()
        assert result == sorted(result)


class TestGetLlms:
    """Tests for get_llms function."""

    def test_returns_list(self) -> None:
        """Test that get_llms returns a list."""
        result = get_llms()
        assert isinstance(result, list)

    def test_has_eight_providers(self) -> None:
        """Test that there are 8 LLM providers."""
        result = get_llms()
        assert len(result) == 8

    def test_contains_openai(self) -> None:
        """Test that OpenAI is in the list."""
        result = get_llms()
        assert "OpenAI" in result

    def test_contains_all_providers(self) -> None:
        """Test that all expected providers are present."""
        result = get_llms()
        expected = ["AI21", "Anthropic", "Cohere", "DeepSeek",
                   "Google", "Groq", "Mistral", "OpenAI"]
        for provider in expected:
            assert provider in result


class TestGetAllCountries:
    """Tests for get_all_countries function."""

    def test_returns_list(self) -> None:
        """Test that get_all_countries returns a list."""
        result = get_all_countries()
        assert isinstance(result, list)

    def test_contains_countries(self) -> None:
        """Test that expected countries are present."""
        result = get_all_countries()
        assert "Nigeria" in result
        assert "China" in result
        assert "Germany" in result

    def test_is_sorted(self) -> None:
        """Test that countries are sorted alphabetically."""
        result = get_all_countries()
        assert result == sorted(result)

    def test_no_duplicates(self) -> None:
        """Test that there are no duplicate countries."""
        result = get_all_countries()
        assert len(result) == len(set(result))


class TestGetCountriesByContinent:
    """Tests for get_countries_by_continent function."""

    def test_africa_has_countries(self) -> None:
        """Test that Africa has countries."""
        result = get_countries_by_continent("Africa")
        assert len(result) > 0
        assert "Nigeria" in result

    def test_case_insensitive(self) -> None:
        """Test that lookup is case-insensitive."""
        result1 = get_countries_by_continent("Africa")
        result2 = get_countries_by_continent("africa")
        result3 = get_countries_by_continent("AFRICA")
        assert result1 == result2 == result3

    def test_invalid_continent_raises(self) -> None:
        """Test that invalid continent raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            get_countries_by_continent("Atlantis")

    def test_returns_copy(self) -> None:
        """Test that returned list is a copy, not original."""
        result1 = get_countries_by_continent("Africa")
        result1.append("FakeCountry")
        result2 = get_countries_by_continent("Africa")
        assert "FakeCountry" not in result2


class TestGetCountriesByLlm:
    """Tests for get_countries_by_llm function."""

    def test_openai_has_countries(self) -> None:
        """Test that OpenAI has countries assigned."""
        result = get_countries_by_llm("OpenAI")
        assert len(result) > 0
        assert "Morocco" in result

    def test_case_insensitive(self) -> None:
        """Test that lookup is case-insensitive."""
        result1 = get_countries_by_llm("OpenAI")
        result2 = get_countries_by_llm("openai")
        result3 = get_countries_by_llm("OPENAI")
        assert result1 == result2 == result3

    def test_invalid_llm_raises(self) -> None:
        """Test that invalid LLM raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            get_countries_by_llm("InvalidLLM")

    def test_all_llms_have_countries(self) -> None:
        """Test that all LLMs have at least some countries."""
        for llm in get_llms():
            result = get_countries_by_llm(llm)
            assert len(result) > 0, f"{llm} has no countries"


class TestGetCountryInfo:
    """Tests for get_country_info function."""

    def test_nigeria_info(self) -> None:
        """Test getting info for Nigeria."""
        result = get_country_info("Nigeria")
        assert isinstance(result, CountryInfo)
        assert result.country == "Nigeria"
        assert result.continent == "Africa"
        assert result.llm == "AI21"

    def test_case_insensitive(self) -> None:
        """Test that lookup is case-insensitive."""
        result1 = get_country_info("Nigeria")
        result2 = get_country_info("nigeria")
        result3 = get_country_info("NIGERIA")
        assert result1.country == result2.country == result3.country

    def test_invalid_country_raises(self) -> None:
        """Test that invalid country raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            get_country_info("FakeCountry")

    def test_germany_info(self) -> None:
        """Test getting info for Germany (Europe)."""
        result = get_country_info("Germany")
        assert result.continent == "Europe"

    def test_china_info(self) -> None:
        """Test getting info for China (Asia)."""
        result = get_country_info("China")
        assert result.continent == "Asia"
        assert result.llm == "AI21"


class TestReloadData:
    """Tests for reload_data function."""

    def test_reload_works(self) -> None:
        """Test that reload_data runs without error."""
        reload_data()
        # After reload, data should still be accessible
        assert len(get_continents()) > 0

    def test_reload_refreshes_cache(self) -> None:
        """Test that reload actually refreshes the cache."""
        # Get initial data
        initial = get_continents()
        # Reload
        reload_data()
        # Get data again
        after = get_continents()
        # Should be same content
        assert initial == after


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_string_continent_raises(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            get_countries_by_continent("")

    def test_empty_string_llm_raises(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            get_countries_by_llm("")

    def test_empty_string_country_raises(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            get_country_info("")
