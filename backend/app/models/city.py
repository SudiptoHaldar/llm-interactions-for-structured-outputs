"""City SQLAlchemy ORM model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.country import Country


class City(Base):
    """City ORM model mapping to cities table."""

    __tablename__ = "cities"

    city_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    country_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("countries.country_id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_capital: Mapped[bool | None] = mapped_column(
        Boolean, default=False, nullable=True
    )
    description: Mapped[str | None] = mapped_column(String(250), nullable=True)
    interesting_fact: Mapped[str | None] = mapped_column(String(250), nullable=True)
    area_sq_mile: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    area_sq_km: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    population: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sci_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    sci_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    numbeo_si: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    numbeo_ci: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    airport_code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    country: Mapped[Country | None] = relationship("Country")

    def __repr__(self) -> str:
        """String representation."""
        return f"<City {self.name}>"
