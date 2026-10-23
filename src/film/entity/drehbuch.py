"""Entity-Klasse für Drehbücher."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from film.entity.base import Base

if TYPE_CHECKING:
    from film.entity.film import Film


class Drehbuch(Base):
    """Drehbuch, das genau einem Film zugeordnet ist."""

    __tablename__ = "drehbuch"

    titel: Mapped[str]
    autor: Mapped[str]
    seitenzahl: Mapped[int]

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )
    film_id: Mapped[int] = mapped_column(
        ForeignKey("film.id", ondelete="CASCADE"),
        unique=True,
        init=False,
    )
    film: Mapped[Film | None] = relationship(
        back_populates="drehbuch",
        default=None,
    )

    @override
    def __repr__(self) -> str:
        return (
        f"Drehbuch(id={self.id}, titel={self.titel},autor={self.autor}"
        f",seitenzahl={self.seitenzahl}, film_id={self.film_id})"
        )
