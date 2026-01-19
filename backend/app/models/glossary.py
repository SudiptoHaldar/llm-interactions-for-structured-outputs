"""Glossary SQLAlchemy ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Glossary(Base):
    """Glossary ORM model mapping to glossary table."""

    __tablename__ = "glossary"

    glossary_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    entry: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    meaning: Mapped[str] = mapped_column(Text, nullable=False)
    range: Mapped[str | None] = mapped_column(String(25), nullable=True)
    interpretation: Mapped[str | None] = mapped_column(String(25), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Glossary {self.entry}>"
