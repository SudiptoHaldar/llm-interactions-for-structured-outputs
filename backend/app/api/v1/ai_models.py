"""AI Models API endpoints."""

from fastapi import APIRouter, HTTPException

from app.crud.ai_model import get_ai_model, get_ai_models
from app.dependencies import DBSession
from app.schemas.ai_model import AIModelListResponse, AIModelResponse

router = APIRouter(tags=["ai-models"])


@router.get("/", response_model=AIModelListResponse)
async def list_ai_models(db: DBSession) -> AIModelListResponse:
    """
    List all AI models.

    Returns all AI models registered in the system.
    """
    ai_models = await get_ai_models(db)
    return AIModelListResponse(
        ai_models=[AIModelResponse.model_validate(m) for m in ai_models],
        count=len(ai_models),
    )


@router.get("/{ai_model_id}", response_model=AIModelResponse)
async def get_ai_model_by_id(ai_model_id: int, db: DBSession) -> AIModelResponse:
    """
    Get AI model by ID.

    Returns a single AI model by its unique identifier.
    """
    ai_model = await get_ai_model(db, ai_model_id)
    if ai_model is None:
        raise HTTPException(status_code=404, detail="AI model not found")
    return AIModelResponse.model_validate(ai_model)
