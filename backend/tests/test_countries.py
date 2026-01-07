"""Tests for countries API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIModel, Continent, Country


@pytest.fixture
async def sample_ai_model(db_session: AsyncSession) -> AIModel:
    """Create a sample AI model for testing."""
    ai_model = AIModel(
        model_provider="OpenAI",
        model_name="gpt-4o",
        description="Test AI model",
        supports_structured_output=True,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(ai_model)
    await db_session.commit()
    await db_session.refresh(ai_model)
    return ai_model


@pytest.fixture
async def sample_continent(
    db_session: AsyncSession, sample_ai_model: AIModel
) -> Continent:
    """Create a sample continent for testing."""
    continent = Continent(
        continent_name="Europe",
        description="Second smallest continent",
        area_sq_mile=3930000.0,
        area_sq_km=10180000.0,
        population=750000000,
        num_country=44,
        ai_model_id=sample_ai_model.ai_model_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(continent)
    await db_session.commit()
    await db_session.refresh(continent)
    return continent


@pytest.fixture
async def sample_country(
    db_session: AsyncSession, sample_continent: Continent, sample_ai_model: AIModel
) -> Country:
    """Create a sample country for testing."""
    country = Country(
        name="Spain",
        description="European country known for diverse landscapes",
        interesting_fact="Home to world's oldest restaurant",
        area_sq_mile=195000,
        area_sq_km=506000,
        population=47400000,
        ppp=47210,
        life_expectancy=82.10,
        travel_risk_level="Level 1",
        global_peace_index_score=1.540,
        global_peace_index_rank=23,
        happiness_index_score=6.930,
        happiness_index_rank=29,
        gdp=1400000000000,
        gdp_growth_rate=2.5,
        inflation_rate=3.2,
        unemployment_rate=12.5,
        govt_debt=118.0,
        credit_rating="A",
        poverty_rate=20.0,
        gini_coefficient=34.7,
        military_spending=1.2,
        continent_id=sample_continent.continent_id,
        ai_model_id=sample_ai_model.ai_model_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(country)
    await db_session.commit()
    await db_session.refresh(country)
    return country


class TestListCountries:
    """Tests for GET /api/v1/countries endpoint."""

    @pytest.mark.asyncio
    async def test_list_countries_empty(self, client: AsyncClient) -> None:
        """Test listing countries when database is empty."""
        response = await client.get("/api/v1/countries/")
        assert response.status_code == 200
        data = response.json()
        assert data["countries"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_list_countries_with_data(
        self, client: AsyncClient, sample_country: Country
    ) -> None:
        """Test listing countries with data."""
        response = await client.get("/api/v1/countries/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["countries"]) == 1
        assert data["countries"][0]["name"] == "Spain"
        assert data["countries"][0]["population"] == 47400000


class TestGetCountryById:
    """Tests for GET /api/v1/countries/{country_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_country_by_id_exists(
        self, client: AsyncClient, sample_country: Country
    ) -> None:
        """Test getting country by ID when it exists."""
        response = await client.get(
            f"/api/v1/countries/{sample_country.country_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Spain"
        assert data["population"] == 47400000
        assert data["life_expectancy"] == 82.10

    @pytest.mark.asyncio
    async def test_get_country_by_id_not_found(self, client: AsyncClient) -> None:
        """Test getting country by ID when it doesn't exist."""
        response = await client.get("/api/v1/countries/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Country not found"


class TestGetCountryByName:
    """Tests for GET /api/v1/countries/name/{country_name} endpoint."""

    @pytest.mark.asyncio
    async def test_get_country_by_name_exists(
        self, client: AsyncClient, sample_country: Country
    ) -> None:
        """Test getting country by name when it exists."""
        response = await client.get("/api/v1/countries/name/Spain")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Spain"

    @pytest.mark.asyncio
    async def test_get_country_by_name_case_insensitive(
        self, client: AsyncClient, sample_country: Country
    ) -> None:
        """Test getting country by name is case-insensitive."""
        response = await client.get("/api/v1/countries/name/spain")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Spain"

    @pytest.mark.asyncio
    async def test_get_country_by_name_not_found(self, client: AsyncClient) -> None:
        """Test getting country by name when it doesn't exist."""
        response = await client.get("/api/v1/countries/name/Atlantis")
        assert response.status_code == 404
        assert response.json()["detail"] == "Country not found"


class TestGetCountriesByContinent:
    """Tests for GET /api/v1/countries/continent/{continent_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_countries_by_continent_id_with_data(
        self, client: AsyncClient, sample_country: Country, sample_continent: Continent
    ) -> None:
        """Test getting countries by continent ID when data exists."""
        response = await client.get(
            f"/api/v1/countries/continent/{sample_continent.continent_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["countries"][0]["name"] == "Spain"

    @pytest.mark.asyncio
    async def test_get_countries_by_continent_id_empty(
        self, client: AsyncClient
    ) -> None:
        """Test getting countries by continent ID when no countries exist."""
        response = await client.get("/api/v1/countries/continent/999")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["countries"] == []


class TestGetCountriesByContinentName:
    """Tests for GET /api/v1/countries/continent/name/{name} endpoint."""

    @pytest.mark.asyncio
    async def test_get_countries_by_continent_name_with_data(
        self, client: AsyncClient, sample_country: Country, sample_continent: Continent
    ) -> None:
        """Test getting countries by continent name when data exists."""
        response = await client.get("/api/v1/countries/continent/name/Europe")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["countries"][0]["name"] == "Spain"

    @pytest.mark.asyncio
    async def test_get_countries_by_continent_name_case_insensitive(
        self, client: AsyncClient, sample_country: Country, sample_continent: Continent
    ) -> None:
        """Test getting countries by continent name is case-insensitive."""
        response = await client.get("/api/v1/countries/continent/name/europe")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1


class TestGetCountriesByModelId:
    """Tests for GET /api/v1/countries/model/{model_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_countries_by_model_id_with_data(
        self, client: AsyncClient, sample_country: Country, sample_ai_model: AIModel
    ) -> None:
        """Test getting countries by AI model ID when data exists."""
        response = await client.get(
            f"/api/v1/countries/model/{sample_ai_model.ai_model_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["countries"][0]["name"] == "Spain"

    @pytest.mark.asyncio
    async def test_get_countries_by_model_id_empty(self, client: AsyncClient) -> None:
        """Test getting countries by model ID when no countries exist."""
        response = await client.get("/api/v1/countries/model/999")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["countries"] == []


class TestGetCountriesByModelName:
    """Tests for GET /api/v1/countries/model/name/{model_name} endpoint."""

    @pytest.mark.asyncio
    async def test_get_countries_by_model_name_with_data(
        self, client: AsyncClient, sample_country: Country, sample_ai_model: AIModel
    ) -> None:
        """Test getting countries by AI model provider name when data exists."""
        response = await client.get("/api/v1/countries/model/name/OpenAI")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["countries"][0]["name"] == "Spain"

    @pytest.mark.asyncio
    async def test_get_countries_by_model_name_case_insensitive(
        self, client: AsyncClient, sample_country: Country, sample_ai_model: AIModel
    ) -> None:
        """Test getting countries by model name is case-insensitive."""
        response = await client.get("/api/v1/countries/model/name/openai")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["countries"][0]["name"] == "Spain"

    @pytest.mark.asyncio
    async def test_get_countries_by_model_name_empty(
        self, client: AsyncClient
    ) -> None:
        """Test getting countries by model name when no countries exist."""
        response = await client.get("/api/v1/countries/model/name/Google")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["countries"] == []
