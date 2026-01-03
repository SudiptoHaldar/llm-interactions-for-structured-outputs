"""Tests for AI models API endpoints."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIModel


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


class TestListAIModels:
    """Tests for GET /api/v1/ai-models endpoint."""

    @pytest.mark.asyncio
    async def test_list_ai_models_empty(self, client: AsyncClient) -> None:
        """Test listing AI models when database is empty."""
        response = await client.get("/api/v1/ai-models/")
        assert response.status_code == 200
        data = response.json()
        assert data["ai_models"] == []
        assert data["count"] == 0

    @pytest.mark.asyncio
    async def test_list_ai_models_with_data(
        self, client: AsyncClient, sample_ai_model: AIModel
    ) -> None:
        """Test listing AI models with data."""
        response = await client.get("/api/v1/ai-models/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["ai_models"]) == 1
        assert data["ai_models"][0]["model_provider"] == "OpenAI"
        assert data["ai_models"][0]["model_name"] == "gpt-4o"


class TestGetAIModelById:
    """Tests for GET /api/v1/ai-models/{ai_model_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_ai_model_by_id_exists(
        self, client: AsyncClient, sample_ai_model: AIModel
    ) -> None:
        """Test getting AI model by ID when it exists."""
        response = await client.get(
            f"/api/v1/ai-models/{sample_ai_model.ai_model_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["model_provider"] == "OpenAI"
        assert data["model_name"] == "gpt-4o"
        assert data["supports_structured_output"] is True

    @pytest.mark.asyncio
    async def test_get_ai_model_by_id_not_found(self, client: AsyncClient) -> None:
        """Test getting AI model by ID when it doesn't exist."""
        response = await client.get("/api/v1/ai-models/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "AI model not found"
