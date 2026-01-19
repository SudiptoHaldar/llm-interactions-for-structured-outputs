"""Country SQLAlchemy ORM model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ai_model import AIModel
    from app.models.continent import Continent


class Country(Base):
    """Country ORM model mapping to countries table."""

    __tablename__ = "countries"

    country_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    ai_model_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ai_models.ai_model_id"), nullable=True
    )
    continent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("continents.continent_id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(250), nullable=True)
    interesting_fact: Mapped[str | None] = mapped_column(String(250), nullable=True)
    area_sq_mile: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    area_sq_km: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    population: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ppp: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    life_expectancy: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    travel_risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    global_peace_index_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 3), nullable=True
    )
    global_peace_index_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    happiness_index_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 3), nullable=True
    )
    happiness_index_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gdp: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    gdp_growth_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    inflation_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    unemployment_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    govt_debt: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    credit_rating: Mapped[str | None] = mapped_column(String(10), nullable=True)
    poverty_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    gini_coefficient: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    military_spending: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
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

    # Relationships
    ai_model: Mapped[AIModel | None] = relationship("AIModel")
    continent: Mapped[Continent | None] = relationship("Continent")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Country {self.name}>"
