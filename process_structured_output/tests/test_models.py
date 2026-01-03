"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from process_structured_output.models.continent import ContinentInfo, ModelIdentity


class TestModelIdentity:
    """Tests for ModelIdentity model."""

    def test_valid_model_identity(self) -> None:
        """Test creating valid ModelIdentity."""
        identity = ModelIdentity(
            model_provider="OpenAI",
            model_name="gpt-4o",
        )
        assert identity.model_provider == "OpenAI"
        assert identity.model_name == "gpt-4o"

    def test_model_identity_max_length(self) -> None:
        """Test ModelIdentity respects max length."""
        # model_provider max is 50
        with pytest.raises(ValidationError):
            ModelIdentity(
                model_provider="x" * 51,
                model_name="gpt-4o",
            )

    def test_model_identity_required_fields(self) -> None:
        """Test ModelIdentity requires all fields."""
        with pytest.raises(ValidationError):
            ModelIdentity(model_provider="OpenAI")  # type: ignore


class TestContinentInfo:
    """Tests for ContinentInfo model."""

    def test_valid_continent_info(self) -> None:
        """Test creating valid ContinentInfo."""
        info = ContinentInfo(
            description="Largest continent by area",
            area_sq_mile=17212000.0,
            area_sq_km=44579000.0,
            population=4700000000,
            num_country=48,
        )
        assert info.description == "Largest continent by area"
        assert info.area_sq_mile == 17212000.0
        assert info.population == 4700000000
        assert info.num_country == 48

    def test_continent_info_positive_values(self) -> None:
        """Test ContinentInfo requires positive values."""
        with pytest.raises(ValidationError):
            ContinentInfo(
                description="Test",
                area_sq_mile=-1.0,
                area_sq_km=1000.0,
                population=1000,
                num_country=10,
            )

    def test_continent_info_description_max_length(self) -> None:
        """Test ContinentInfo respects description max length."""
        with pytest.raises(ValidationError):
            ContinentInfo(
                description="x" * 251,
                area_sq_mile=1000.0,
                area_sq_km=1000.0,
                population=1000,
                num_country=10,
            )

    def test_continent_info_zero_countries_allowed(self) -> None:
        """Test ContinentInfo allows zero countries (e.g., Antarctica)."""
        info = ContinentInfo(
            description="Frozen continent with no countries",
            area_sq_mile=5400000.0,
            area_sq_km=14000000.0,
            population=1000,
            num_country=0,
        )
        assert info.num_country == 0
