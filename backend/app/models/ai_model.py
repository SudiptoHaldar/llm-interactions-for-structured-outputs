"""AIModel SQLAlchemy ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.continent import Continent


class AIModel(Base):
    """AI Model ORM model mapping to ai_models table."""

    __tablename__ = "ai_models"

    ai_model_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    model_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(250), nullable=True)
    supports_structured_output: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship to continents
    continents: Mapped[list[Continent]] = relationship(
        "Continent", back_populates="ai_model"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<AIModel {self.model_provider}/{self.model_name}>"
