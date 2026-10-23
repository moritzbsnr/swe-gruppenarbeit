"""Entity-Klasse für Schauspieler."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from film.entity.base import Base

if TYPE_CHECKING:
    from film.entity.film import Film


class Schauspieler(Base):
    """Schauspieler, der genau einem Film zugeordnet ist."""

    __tablename__ = "schauspieler"

    vorname: Mapped[str]
    nachname: Mapped[str]

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )

    film_id: Mapped[int] = mapped_column(
        ForeignKey("film.id", ondelete="CASCADE"),
        init=False,
    )
    film: Mapped[Film | None] = relationship(
        back_populates="schauspieler",
        default=None,
    )

    @override
    def __repr__(self) -> str:
        return f"Schauspieler(id={self.id}, name={self.vorname} {self.nachname})"
