"""Tests for continents API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIModel, Continent


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
        continent_name="Africa",
        description="Second largest continent by area and population",
        area_sq_mile=11668599.0,
        area_sq_km=30221532.0,
        population=1400000000,
        num_country=54,
        ai_model_id=sample_ai_model.ai_model_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db_session.add(continent)
    await db_session.commit()
    await db_session.refresh(continent)
    return continent


class TestListContinents:
    """Tests for GET /api/v1/continents endpoint."""

    @pytest.mark.asyncio
    async def test_list_continents_empty(self, client: AsyncClient) -> None:
        """Test listing continents when database is empty."""
        response = await client.get("/api/v1/continents/")
        assert response.status_code == 200
        data = response.json()
        assert data["continents"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_list_continents_with_data(
        self, client: AsyncClient, sample_continent: Continent
    ) -> None:
        """Test listing continents with data."""
        response = await client.get("/api/v1/continents/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["continents"]) == 1
        assert data["continents"][0]["continent_name"] == "Africa"
        assert data["continents"][0]["num_country"] == 54


class TestGetContinentById:
    """Tests for GET /api/v1/continents/{continent_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_continent_by_id_exists(
        self, client: AsyncClient, sample_continent: Continent
    ) -> None:
        """Test getting continent by ID when it exists."""
        response = await client.get(
            f"/api/v1/continents/{sample_continent.continent_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["continent_name"] == "Africa"
        assert data["population"] == 1400000000

    @pytest.mark.asyncio
    async def test_get_continent_by_id_not_found(self, client: AsyncClient) -> None:
        """Test getting continent by ID when it doesn't exist."""
        response = await client.get("/api/v1/continents/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Continent not found"


class TestGetContinentByName:
    """Tests for GET /api/v1/continents/name/{continent_name} endpoint."""

    @pytest.mark.asyncio
    async def test_get_continent_by_name_exists(
        self, client: AsyncClient, sample_continent: Continent
    ) -> None:
        """Test getting continent by name when it exists."""
        response = await client.get("/api/v1/continents/name/Africa")
        assert response.status_code == 200
        data = response.json()
        assert data["continent_name"] == "Africa"

    @pytest.mark.asyncio
    async def test_get_continent_by_name_case_insensitive(
        self, client: AsyncClient, sample_continent: Continent
    ) -> None:
        """Test getting continent by name is case-insensitive."""
        response = await client.get("/api/v1/continents/name/africa")
        assert response.status_code == 200
        data = response.json()
        assert data["continent_name"] == "Africa"

    @pytest.mark.asyncio
    async def test_get_continent_by_name_not_found(self, client: AsyncClient) -> None:
        """Test getting continent by name when it doesn't exist."""
        response = await client.get("/api/v1/continents/name/Atlantis")
        assert response.status_code == 404
        assert response.json()["detail"] == "Continent not found"
