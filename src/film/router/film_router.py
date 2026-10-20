"""REST-Endpunkte für Filme, Schauspieler und Drehbücher."""

from datetime import date
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from film.entity import Drehbuch, Film, Schauspieler
from film.repository.session_factory import Session

router = APIRouter(prefix="/filme", tags=["Filme"])


class SchauspielerInput(BaseModel):
    """Eingabedaten für einen Schauspieler eines Films."""

    vorname: str = Field(min_length=1)
    nachname: str = Field(min_length=1)
    geburtsdatum: date


class DrehbuchInput(BaseModel):
    """Eingabedaten für das Drehbuch eines Films."""

    titel: str = Field(min_length=1)
    autor: str = Field(min_length=1)
    inhalt: str = Field(min_length=1)


class FilmInput(BaseModel):
    """Eingabedaten für Film samt Besetzung und Drehbuch."""

    titel: str = Field(min_length=1)
    erscheinungsjahr: int = Field(gt=1888)
    genre: str = Field(min_length=1)
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
    erscheinungsjahr: int
    genre: str
    schauspieler: list[SchauspielerOutput]
    drehbuch: DrehbuchOutput


@router.get("", response_model=list[FilmOutput])
def get_filme() -> list[FilmOutput]:
    """Alle Filme mit ihren Schauspielern und Drehbüchern lesen."""
    with Session() as session:
        filme = session.scalars(select(Film)).all()
        return [FilmOutput.model_validate(film) for film in filme]


@router.get("/{film_id}", response_model=FilmOutput)
def get_film(film_id: int) -> FilmOutput:
    """Einen Film anhand seiner ID lesen."""
    with Session() as session:
        film = session.get(Film, film_id)
        if film is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return FilmOutput.model_validate(film)


@router.post("", response_model=FilmOutput, status_code=status.HTTP_201_CREATED)
def create_film(film_input: FilmInput) -> FilmOutput:
    """Einen Film mit Schauspielern und genau einem Drehbuch anlegen."""
    film = Film(
        titel=film_input.titel,
        erscheinungsjahr=film_input.erscheinungsjahr,
        genre=film_input.genre,
        schauspieler=[
            Schauspieler(**actor.model_dump()) for actor in film_input.schauspieler
        ],
        drehbuch=Drehbuch(**film_input.drehbuch.model_dump()),
    )
    with Session() as session:
        session.add(film)
        session.commit()
        session.refresh(film)
        return FilmOutput.model_validate(film)
