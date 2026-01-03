"""Tests for health check endpoint."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test suite for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check_returns_healthy(self, client: AsyncClient) -> None:
        """Test health check returns healthy status."""
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "database" in data

    @pytest.mark.asyncio
    async def test_liveness_probe(self, client: AsyncClient) -> None:
        """Test liveness probe returns alive status."""
        response = await client.get("/api/v1/health/live")

        assert response.status_code == 200
        assert response.json() == {"status": "alive"}

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient) -> None:
        """Test root endpoint returns welcome message."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome" in data["message"]
