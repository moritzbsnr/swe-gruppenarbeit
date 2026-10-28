"""Geschäftslogik zum Schreiben von Filmdaten."""

from typing import Final
lazy from datetime import date

from loguru import logger

from film.repository import FilmRepository, Session
from film.service.exceptions import (
    DrehbuchRequiredError,
    NotFoundError,
)
from film.service.film_dto import FilmDTO
lazy from film.entity import Film

__all__ = ["FilmWriteService"]


class FilmWriteService:
    """Service zum Anlegen, Ändern und Löschen von Filmen."""

    def __init__(self, repo: FilmRepository) -> None:
        """Initialisiert den Service mit dem Film-Repository."""
        self.repo = repo

    def create(self, film: Film) -> FilmDTO:
        """Legt einen Film samt Drehbuch und Schauspielern an."""
        logger.debug("film={}", film)
        if film.drehbuch is None:
            raise DrehbuchRequiredError

        with Session() as session:
            created: Final = self.repo.create(film=film, session=session)
            film_dto: Final = FilmDTO.from_film(created)
            session.commit()
        return film_dto

    def update(
        self,
        film_id: int,
        titel: str | None,
        erscheinungsjahr: date | None,
    ) -> FilmDTO:
        """Aktualisiert angegebene Felder und behält ausgelassene unverändert."""
        logger.debug(
            "film_id={}, titel={}, erscheinungsjahr={}",
            film_id,
            titel,
            erscheinungsjahr,
        )
        with Session() as session:
            film_db = self.repo.find_by_id(film_id=film_id, session=session)
            if film_db is None:
                raise NotFoundError(film_id=film_id)

            if titel is not None:
                film_db.titel = titel
            if erscheinungsjahr is not None:
                film_db.erscheinungsjahr = erscheinungsjahr

            session.flush()
            film_dto: Final = FilmDTO.from_film(film_db)
            session.commit()
        return film_dto

    def delete_by_id(self, film_id: int) -> None:
        """Löscht einen Film samt Drehbuch und Schauspielern."""
        logger.debug("film_id={}", film_id)
        with Session() as session:
            if self.repo.find_by_id(film_id=film_id, session=session) is None:
                raise NotFoundError(film_id=film_id)

            self.repo.delete_by_id(film_id=film_id, session=session)
            session.commit()
