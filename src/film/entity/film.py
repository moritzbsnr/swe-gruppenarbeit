"""Entity-Klasse für Filme."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from sqlalchemy import Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from film.entity.base import Base

if TYPE_CHECKING:
    from film.entity.drehbuch import Drehbuch
    from film.entity.schauspieler import Schauspieler


class Film(Base):
    """Film mit mehreren Schauspielern und genau einem Drehbuch."""

    __tablename__ = "film"

    titel: Mapped[str]
    erscheinungsjahr: Mapped[int]

    id: Mapped[int | None] = mapped_column(
        Identity(start=1000),
        primary_key=True,
    )

    drehbuch: Mapped[Drehbuch] = relationship(
        back_populates="film",
        uselist=False,
        cascade="all, delete-orphan",
    )

    schauspieler: Mapped[list[Schauspieler]] = relationship(
        back_populates="film",
        default_factory=list,
        cascade="all, delete-orphan",
    )

    @override
    def __repr__(self) -> str:
        return f"Film(id={self.id}, titel={self.titel}, jahr={self.erscheinungsjahr})"
