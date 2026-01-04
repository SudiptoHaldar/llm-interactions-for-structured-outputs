"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from process_structured_output.models.continent import ContinentInfo, ModelIdentity
from process_structured_output.models.country import (
    CitiesResponse,
    CityInfo,
    CountryInfo,
)


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


class TestCountryInfo:
    """Tests for CountryInfo model."""

    def test_valid_country_info(self) -> None:
        """Test creating valid CountryInfo."""
        info = CountryInfo(
            description="West African nation",
            interesting_fact="Most populous country in Africa",
            area_sq_mile=356669.0,
            area_sq_km=923768.0,
            population=220000000,
            ppp=5500.0,
            life_expectancy=55.0,
            travel_risk_level="Level 3",
            global_peace_index_score=2.7,
            global_peace_index_rank=144,
            happiness_index_score=4.5,
            happiness_index_rank=99,
            gdp=450000000000.0,
            gdp_growth_rate=3.5,
            inflation_rate=18.0,
            unemployment_rate=5.0,
            govt_debt=38.0,
            credit_rating="B-",
            poverty_rate=40.0,
            gini_coefficient=35.0,
            military_spending=0.6,
        )
        assert info.description == "West African nation"
        assert info.population == 220000000
        assert info.gdp == 450000000000.0

    def test_country_info_positive_values(self) -> None:
        """Test CountryInfo requires positive values for area."""
        with pytest.raises(ValidationError):
            CountryInfo(
                description="Test",
                interesting_fact="Test",
                area_sq_mile=-1.0,  # Invalid: must be > 0
                area_sq_km=1000.0,
                population=1000,
                ppp=1000.0,
                life_expectancy=70.0,
                travel_risk_level="Level 1",
                global_peace_index_score=1.0,
                global_peace_index_rank=1,
                happiness_index_score=5.0,
                happiness_index_rank=1,
                gdp=1000.0,
                gdp_growth_rate=1.0,
                inflation_rate=1.0,
                unemployment_rate=1.0,
                govt_debt=1.0,
                credit_rating="AAA",
                poverty_rate=1.0,
                gini_coefficient=30.0,
                military_spending=1.0,
            )

    def test_country_info_description_max_length(self) -> None:
        """Test CountryInfo respects description max length."""
        with pytest.raises(ValidationError):
            CountryInfo(
                description="x" * 251,  # Invalid: max 250
                interesting_fact="Test",
                area_sq_mile=1000.0,
                area_sq_km=1000.0,
                population=1000,
                ppp=1000.0,
                life_expectancy=70.0,
                travel_risk_level="Level 1",
                global_peace_index_score=1.0,
                global_peace_index_rank=1,
                happiness_index_score=5.0,
                happiness_index_rank=1,
                gdp=1000.0,
                gdp_growth_rate=1.0,
                inflation_rate=1.0,
                unemployment_rate=1.0,
                govt_debt=1.0,
                credit_rating="AAA",
                poverty_rate=1.0,
                gini_coefficient=30.0,
                military_spending=1.0,
            )


class TestCityInfo:
    """Tests for CityInfo model."""

    def test_valid_city_info(self) -> None:
        """Test creating valid CityInfo."""
        info = CityInfo(
            name="Lagos",
            is_capital=False,
            description="Economic hub of Nigeria",
            interesting_fact="Most populous city in Africa",
            area_sq_mile=452.0,
            area_sq_km=1171.0,
            population=15000000,
            sci_score=None,
            sci_rank=None,
            numbeo_si=35.0,
            numbeo_ci=65.0,
            airport_code="LOS",
        )
        assert info.name == "Lagos"
        assert info.is_capital is False
        assert info.population == 15000000
        assert info.airport_code == "LOS"

    def test_city_info_airport_code_length(self) -> None:
        """Test CityInfo requires 3-letter airport code."""
        with pytest.raises(ValidationError):
            CityInfo(
                name="Lagos",
                is_capital=False,
                description="Test",
                interesting_fact="Test",
                area_sq_mile=452.0,
                area_sq_km=1171.0,
                population=15000000,
                airport_code="LA",  # Invalid: must be 3 letters
            )

    def test_city_info_optional_safety_indices(self) -> None:
        """Test CityInfo allows None for safety indices."""
        info = CityInfo(
            name="Lagos",
            is_capital=False,
            description="Test",
            interesting_fact="Test",
            area_sq_mile=452.0,
            area_sq_km=1171.0,
            population=15000000,
            sci_score=None,
            sci_rank=None,
            numbeo_si=None,
            numbeo_ci=None,
            airport_code="LOS",
        )
        assert info.sci_score is None
        assert info.numbeo_si is None


class TestCitiesResponse:
    """Tests for CitiesResponse model."""

    def test_valid_cities_response(self) -> None:
        """Test creating valid CitiesResponse."""
        city = CityInfo(
            name="Lagos",
            is_capital=False,
            description="Economic hub",
            interesting_fact="Largest city",
            area_sq_mile=452.0,
            area_sq_km=1171.0,
            population=15000000,
            airport_code="LOS",
        )
        response = CitiesResponse(cities=[city])
        assert len(response.cities) == 1
        assert response.cities[0].name == "Lagos"

    def test_cities_response_max_length(self) -> None:
        """Test CitiesResponse respects max 5 cities."""
        cities = [
            CityInfo(
                name=f"City{i}",
                is_capital=False,
                description="Test",
                interesting_fact="Test",
                area_sq_mile=100.0,
                area_sq_km=259.0,
                population=1000000,
                airport_code="XXX",
            )
            for i in range(6)  # 6 cities exceeds max of 5
        ]
        with pytest.raises(ValidationError):
            CitiesResponse(cities=cities)
