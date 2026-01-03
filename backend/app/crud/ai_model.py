"""CRUD operations for AI models."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_model import AIModel


async def get_ai_model(db: AsyncSession, ai_model_id: int) -> AIModel | None:
    """Get AI model by ID."""
    result = await db.execute(select(AIModel).where(AIModel.ai_model_id == ai_model_id))
    return result.scalar_one_or_none()


async def get_ai_models(db: AsyncSession) -> list[AIModel]:
    """Get all AI models."""
    result = await db.execute(select(AIModel).order_by(AIModel.ai_model_id))
    return list(result.scalars().all())
