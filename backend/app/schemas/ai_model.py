"""AI Model Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIModelResponse(BaseModel):
    """AI Model response schema."""

    model_config = ConfigDict(from_attributes=True)

    ai_model_id: int
    model_provider: str
    model_name: str
    description: str | None
    supports_structured_output: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AIModelListResponse(BaseModel):
    """AI Model list response schema."""

    ai_models: list[AIModelResponse]
    count: int
