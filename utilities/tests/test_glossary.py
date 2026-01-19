"""Tests for glossary module."""

import pytest

from utilities.glossary import (
    GlossaryEntry,
    get_entry,
    get_glossary_entries,
    reload_entries,
)


class TestGetGlossaryEntries:
    """Tests for get_glossary_entries function."""

    def test_returns_list(self) -> None:
        """Test that get_glossary_entries returns a list."""
        result = get_glossary_entries()
        assert isinstance(result, list)

    def test_contains_entries(self) -> None:
        """Test that entries are present."""
        result = get_glossary_entries()
        assert len(result) > 0

    def test_has_eight_entries(self) -> None:
        """Test that there are 8 glossary entries."""
        result = get_glossary_entries()
        assert len(result) == 8

    def test_entries_are_glossary_entry_objects(self) -> None:
        """Test that all entries are GlossaryEntry objects."""
        result = get_glossary_entries()
        for entry in result:
            assert isinstance(entry, GlossaryEntry)

    def test_returns_copy(self) -> None:
        """Test that returned list is a copy, not original."""
        result1 = get_glossary_entries()
        result1.append(
            GlossaryEntry(
                entry="Fake",
                meaning="Fake meaning",
                range=None,
                interpretation=None,
            )
        )
        result2 = get_glossary_entries()
        assert len(result2) == 8


class TestGetEntry:
    """Tests for get_entry function."""

    def test_gini_coefficient(self) -> None:
        """Test getting Gini Coefficient entry."""
        result = get_entry("Gini Coefficient")
        assert isinstance(result, GlossaryEntry)
        assert result.entry == "Gini Coefficient"
        assert result.interpretation == "Lower is better"

    def test_ppp_entry(self) -> None:
        """Test getting PPP (Purchasing Power Parity) entry."""
        result = get_entry("PPP (Purchasing Power Parity)")
        assert result.entry == "PPP (Purchasing Power Parity)"
        assert result.range == "Numeric"

    def test_gpi_entry(self) -> None:
        """Test getting GPI (Global Peace Index) entry."""
        result = get_entry("GPI (Global Peace Index)")
        assert result.entry == "GPI (Global Peace Index)"
        assert result.range == "1 - 5"
        assert result.interpretation == "Lower is better"

    def test_happiness_index(self) -> None:
        """Test getting Happiness Index entry."""
        result = get_entry("Happiness Index")
        assert result.entry == "Happiness Index"
        assert result.range == "0 - 10"
        assert result.interpretation == "Higher is better"

    def test_case_insensitive(self) -> None:
        """Test that lookup is case-insensitive."""
        result1 = get_entry("Gini Coefficient")
        result2 = get_entry("gini coefficient")
        result3 = get_entry("GINI COEFFICIENT")
        assert result1.entry == result2.entry == result3.entry

    def test_invalid_entry_raises(self) -> None:
        """Test that invalid entry raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            get_entry("Invalid Entry")

    def test_empty_string_raises(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            get_entry("")


class TestReloadEntries:
    """Tests for reload_entries function."""

    def test_reload_works(self) -> None:
        """Test that reload_entries runs without error."""
        reload_entries()
        # After reload, data should still be accessible
        assert len(get_glossary_entries()) > 0

    def test_reload_refreshes_cache(self) -> None:
        """Test that reload actually refreshes the cache."""
        # Get initial data
        initial = get_glossary_entries()
        # Reload
        reload_entries()
        # Get data again
        after = get_glossary_entries()
        # Should be same content
        assert len(initial) == len(after)


class TestGlossaryEntryDataclass:
    """Tests for GlossaryEntry dataclass."""

    def test_entry_has_required_fields(self) -> None:
        """Test that GlossaryEntry has required fields."""
        entry = get_entry("PPP (Purchasing Power Parity)")
        assert hasattr(entry, "entry")
        assert hasattr(entry, "meaning")
        assert hasattr(entry, "range")
        assert hasattr(entry, "interpretation")

    def test_entry_field_types(self) -> None:
        """Test that GlossaryEntry fields have correct types."""
        entry = get_entry("Gini Coefficient")
        assert isinstance(entry.entry, str)
        assert isinstance(entry.meaning, str)
        # range and interpretation can be str or None
        assert entry.range is None or isinstance(entry.range, str)
        assert entry.interpretation is None or isinstance(entry.interpretation, str)

    def test_meaning_is_not_empty(self) -> None:
        """Test that meaning is never empty."""
        entries = get_glossary_entries()
        for entry in entries:
            assert entry.meaning
            assert len(entry.meaning) > 0


class TestMeaningContent:
    """Tests for meaning content validation."""

    def test_gini_meaning_contains_inequality(self) -> None:
        """Test that Gini meaning mentions inequality."""
        entry = get_entry("Gini Coefficient")
        assert "inequality" in entry.meaning.lower()

    def test_ppp_meaning_contains_cost(self) -> None:
        """Test that PPP meaning mentions cost of goods."""
        entry = get_entry("PPP (Purchasing Power Parity)")
        assert "cost" in entry.meaning.lower()

    def test_gpi_meaning_contains_peace(self) -> None:
        """Test that GPI meaning mentions peace."""
        entry = get_entry("GPI (Global Peace Index)")
        assert "peace" in entry.meaning.lower()

    def test_happiness_meaning_contains_quality(self) -> None:
        """Test that Happiness Index meaning mentions quality of life."""
        entry = get_entry("Happiness Index")
        meaning_lower = entry.meaning.lower()
        assert "quality of life" in meaning_lower


class TestEdgeCases:
    """Tests for edge cases."""

    def test_whitespace_in_name_handled(self) -> None:
        """Test that entries with whitespace work correctly."""
        # Gini Coefficient and Happiness Index both have spaces
        result1 = get_entry("Gini Coefficient")
        result2 = get_entry("Happiness Index")
        assert result1.entry == "Gini Coefficient"
        assert result2.entry == "Happiness Index"

    def test_all_entries_have_valid_range_or_none(self) -> None:
        """Test that range is either a valid string or None."""
        entries = get_glossary_entries()
        for entry in entries:
            if entry.range is not None:
                assert len(entry.range) > 0

    def test_all_entries_have_valid_interpretation_or_none(self) -> None:
        """Test that interpretation is either a valid string or None."""
        entries = get_glossary_entries()
        for entry in entries:
            if entry.interpretation is not None:
                assert len(entry.interpretation) > 0
