"""REST-Endpunkte für Filme, Schauspieler und Drehbücher."""

lazy from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from film.entity import Film
from film.repository.session_factory import Session

router = APIRouter(prefix="/filme", tags=["Filme"])


class SchauspielerInput(BaseModel):
    """Eingabedaten für einen Schauspieler eines Films."""

    vorname: str = Field(min_length=1)
    nachname: str = Field(min_length=1)


class DrehbuchInput(BaseModel):
    """Eingabedaten für das Drehbuch eines Films."""

    titel: str = Field(min_length=1)
    autor: str = Field(min_length=1)
    seitenzahl: int = Field(gt=0)


class FilmInput(BaseModel):
    """Eingabedaten für Film samt Besetzung und Drehbuch."""

    titel: str = Field(min_length=1)
    erscheinungsjahr: date
    schauspieler: list[SchauspielerInput] = Field(min_length=1)
    drehbuch: DrehbuchInput


class SchauspielerOutput(SchauspielerInput):
    """Ausgabedaten für Schauspieler."""

    model_config = ConfigDict(from_attributes=True)
    id: int


class DrehbuchOutput(DrehbuchInput):
    """Ausgabedaten für Drehbuch."""

    model_config = ConfigDict(from_attributes=True)
    id: int


class FilmOutput(BaseModel):
    """Ausgabedaten für Film samt Schauspielern und Drehbuch."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    titel: str
    erscheinungsjahr: date
    schauspieler: list[SchauspielerOutput]
    drehbuch: DrehbuchOutput


@router.get("", response_model=list[FilmOutput])
def get_filme() -> list[FilmOutput]:
    """Alle Filme mit ihren Schauspielern und Drehbüchern lesen."""
    with Session() as session:
        filme = session.scalars(select(Film)).all()
        return [FilmOutput.model_validate(film) for film in filme]


@router.get("/{film_id}", response_model=FilmOutput)
def get_by_id(film_id: int) -> FilmOutput:
    """Einen Film anhand seiner ID lesen."""
    with Session() as session:
        film = session.get(Film, film_id)
        if film is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return FilmOutput.model_validate(film)
