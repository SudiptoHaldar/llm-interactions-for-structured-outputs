"""Glossary API endpoints."""

from fastapi import APIRouter, HTTPException

from app.crud.glossary import (
    get_all_glossary_entries,
    get_glossary_entry,
    get_glossary_entry_by_name,
)
from app.dependencies import DBSession
from app.schemas.glossary import GlossaryListResponse, GlossaryResponse

router = APIRouter(tags=["glossary"])


@router.get("/", response_model=GlossaryListResponse)
async def list_glossary_entries(db: DBSession) -> GlossaryListResponse:
    """
    List all glossary entries.

    Returns all glossary entries stored in the database, ordered by entry name.
    """
    entries = await get_all_glossary_entries(db)
    return GlossaryListResponse(
        glossary=[GlossaryResponse.model_validate(e) for e in entries],
        count=len(entries),
    )


@router.get("/{glossary_id}", response_model=GlossaryResponse)
async def get_glossary_by_id(glossary_id: int, db: DBSession) -> GlossaryResponse:
    """
    Get glossary entry by ID.

    Returns a single glossary entry by its unique identifier.
    """
    entry = await get_glossary_entry(db, glossary_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Glossary entry not found")
    return GlossaryResponse.model_validate(entry)


@router.get("/entry/{entry_name}", response_model=GlossaryResponse)
async def get_glossary_by_entry_name(
    entry_name: str, db: DBSession
) -> GlossaryResponse:
    """
    Get glossary entry by entry name.

    Returns a single glossary entry by its name (case-insensitive).
    """
    entry = await get_glossary_entry_by_name(db, entry_name)
    if entry is None:
        raise HTTPException(status_code=404, detail="Glossary entry not found")
    return GlossaryResponse.model_validate(entry)
