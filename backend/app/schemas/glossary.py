"""Glossary Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GlossaryResponse(BaseModel):
    """Glossary response schema."""

    model_config = ConfigDict(from_attributes=True)

    glossary_id: int
    entry: str
    meaning: str
    range: str | None
    interpretation: str | None
    created_at: datetime
    updated_at: datetime


class GlossaryListResponse(BaseModel):
    """Glossary list response schema."""

    glossary: list[GlossaryResponse]
    count: int
