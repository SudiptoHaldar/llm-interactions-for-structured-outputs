"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import ai_models, continents, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(continents.router, prefix="/continents")
api_router.include_router(ai_models.router, prefix="/ai-models")
