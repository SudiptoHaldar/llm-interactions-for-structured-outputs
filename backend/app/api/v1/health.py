"""Health check endpoint."""

from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.dependencies import DBSession
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: DBSession) -> HealthResponse:
    """
    Health check endpoint.

    Returns application status, version, and database connectivity.
    """
    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        database=db_status,
    )


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    """Liveness probe for Kubernetes."""
    return {"status": "alive"}
