"""Continent SQLAlchemy ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ai_model import AIModel


class Continent(Base):
    """Continent ORM model mapping to continents table."""

    __tablename__ = "continents"

    continent_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    continent_name: Mapped[str] = mapped_column(
        "name", String(100), unique=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(250), nullable=True)
    area_sq_mile: Mapped[float | None] = mapped_column(Float, nullable=True)
    area_sq_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    population: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    num_country: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_model_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ai_models.ai_model_id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship to AI model
    ai_model: Mapped[AIModel | None] = relationship(
        "AIModel", back_populates="continents"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Continent {self.continent_name}>"
