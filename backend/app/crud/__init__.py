"""CRUD operations package."""

from app.crud.ai_model import get_ai_model, get_ai_models
from app.crud.continent import get_continent, get_continent_by_name, get_continents

__all__ = [
    "get_ai_model",
    "get_ai_models",
    "get_continent",
    "get_continent_by_name",
    "get_continents",
]
