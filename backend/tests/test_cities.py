"""Tests for cities API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIModel, City, Continent, Country


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
        continent_id=sample_continent.continent_id,
        ai_model_id=sample_ai_model.ai_model_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(country)
    await db_session.commit()
    await db_session.refresh(country)
    return country


@pytest.fixture
async def sample_city(db_session: AsyncSession, sample_country: Country) -> City:
    """Create a sample city for testing."""
    city = City(
        name="Madrid",
        is_capital=True,
        description="Capital and largest city of Spain",
        interesting_fact="Home to the world-famous Prado Museum",
        area_sq_mile=233.30,
        area_sq_km=604.30,
        population=3200000,
        sci_score=82.4,
        sci_rank=23,
        numbeo_si=86.8,
        numbeo_ci=27.2,
        airport_code="MAD",
        country_id=sample_country.country_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(city)
    await db_session.commit()
    await db_session.refresh(city)
    return city


class TestListCities:
    """Tests for GET /api/v1/cities endpoint."""

    @pytest.mark.asyncio
    async def test_list_cities_empty(self, client: AsyncClient) -> None:
        """Test listing cities when database is empty."""
        response = await client.get("/api/v1/cities/")
        assert response.status_code == 200
        data = response.json()
        assert data["cities"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_list_cities_with_data(
        self, client: AsyncClient, sample_city: City
    ) -> None:
        """Test listing cities with data."""
        response = await client.get("/api/v1/cities/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["cities"]) == 1
        assert data["cities"][0]["name"] == "Madrid"
        assert data["cities"][0]["population"] == 3200000


class TestGetCityById:
    """Tests for GET /api/v1/cities/{city_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_city_by_id_exists(
        self, client: AsyncClient, sample_city: City
    ) -> None:
        """Test getting city by ID when it exists."""
        response = await client.get(f"/api/v1/cities/{sample_city.city_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Madrid"
        assert data["population"] == 3200000
        assert data["is_capital"] is True

    @pytest.mark.asyncio
    async def test_get_city_by_id_not_found(self, client: AsyncClient) -> None:
        """Test getting city by ID when it doesn't exist."""
        response = await client.get("/api/v1/cities/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "City not found"


class TestGetCityByName:
    """Tests for GET /api/v1/cities/name/{city_name} endpoint."""

    @pytest.mark.asyncio
    async def test_get_city_by_name_exists(
        self, client: AsyncClient, sample_city: City
    ) -> None:
        """Test getting city by name when it exists."""
        response = await client.get("/api/v1/cities/name/Madrid")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Madrid"

    @pytest.mark.asyncio
    async def test_get_city_by_name_case_insensitive(
        self, client: AsyncClient, sample_city: City
    ) -> None:
        """Test getting city by name is case-insensitive."""
        response = await client.get("/api/v1/cities/name/madrid")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Madrid"

    @pytest.mark.asyncio
    async def test_get_city_by_name_not_found(self, client: AsyncClient) -> None:
        """Test getting city by name when it doesn't exist."""
        response = await client.get("/api/v1/cities/name/Atlantis")
        assert response.status_code == 404
        assert response.json()["detail"] == "City not found"


class TestGetCitiesByCountryId:
    """Tests for GET /api/v1/cities/country/{country_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_cities_by_country_id_with_data(
        self, client: AsyncClient, sample_city: City, sample_country: Country
    ) -> None:
        """Test getting cities by country ID when data exists."""
        response = await client.get(
            f"/api/v1/cities/country/{sample_country.country_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["cities"][0]["name"] == "Madrid"

    @pytest.mark.asyncio
    async def test_get_cities_by_country_id_empty(self, client: AsyncClient) -> None:
        """Test getting cities by country ID when no cities exist."""
        response = await client.get("/api/v1/cities/country/999")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["cities"] == []


class TestGetCitiesByCountryName:
    """Tests for GET /api/v1/cities/country/name/{country_name} endpoint."""

    @pytest.mark.asyncio
    async def test_get_cities_by_country_name_with_data(
        self, client: AsyncClient, sample_city: City, sample_country: Country
    ) -> None:
        """Test getting cities by country name when data exists."""
        response = await client.get("/api/v1/cities/country/name/Spain")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["cities"][0]["name"] == "Madrid"

    @pytest.mark.asyncio
    async def test_get_cities_by_country_name_case_insensitive(
        self, client: AsyncClient, sample_city: City, sample_country: Country
    ) -> None:
        """Test getting cities by country name is case-insensitive."""
        response = await client.get("/api/v1/cities/country/name/spain")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["cities"][0]["name"] == "Madrid"

    @pytest.mark.asyncio
    async def test_get_cities_by_country_name_empty(self, client: AsyncClient) -> None:
        """Test getting cities by country name when no cities exist."""
        response = await client.get("/api/v1/cities/country/name/Atlantis")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["cities"] == []
