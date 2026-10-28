"""DTOs für Filme und die zugehörigen Beziehungen."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
lazy from datetime import date

import strawberry

from film.service.exceptions import DrehbuchRequiredError

if TYPE_CHECKING:
    from film.entity import Drehbuch, Film, Schauspieler

__all__ = ["DrehbuchDTO", "FilmDTO", "SchauspielerDTO"]


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="Drehbuch")
class DrehbuchDTO:
    """DTO für ein Filmdrehbuch."""

    id: int
    titel: str
    autor: str
    seitenzahl: int

    @classmethod
    def from_drehbuch(cls, drehbuch: Drehbuch) -> DrehbuchDTO:
        """Erstellt das DTO aus einem Drehbuch."""
        return cls(
            id=drehbuch.id if drehbuch.id is not None else -1,
            titel=drehbuch.titel,
            autor=drehbuch.autor,
            seitenzahl=drehbuch.seitenzahl,
        )


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="Schauspieler")
class SchauspielerDTO:
    """DTO für einen Schauspieler."""

    id: int
    vorname: str
    nachname: str

    @classmethod
    def from_schauspieler(cls, schauspieler: Schauspieler) -> SchauspielerDTO:
        """Erstellt das DTO aus einem Schauspieler."""
        return cls(
            id=schauspieler.id if schauspieler.id is not None else -1,
            vorname=schauspieler.vorname,
            nachname=schauspieler.nachname,
        )


@dataclass(eq=False, slots=True, kw_only=True)
@strawberry.type(name="Film")
class FilmDTO:
    """DTO für einen Film mit genau einem Drehbuch und mehreren Schauspielern."""

    id: int
    titel: str
    erscheinungsjahr: date
    drehbuch: DrehbuchDTO
    schauspieler: list[SchauspielerDTO]

    @classmethod
    def from_film(cls, film: Film) -> FilmDTO:
        """Erstellt das Film-DTO inklusive aller Beziehungen."""
        if film.drehbuch is None:
            raise DrehbuchRequiredError

        return cls(
            id=film.id if film.id is not None else -1,
            titel=film.titel,
            erscheinungsjahr=film.erscheinungsjahr,
            drehbuch=DrehbuchDTO.from_drehbuch(film.drehbuch),
            schauspieler=[
                SchauspielerDTO.from_schauspieler(schauspieler)
                for schauspieler in film.schauspieler
            ],
        )
