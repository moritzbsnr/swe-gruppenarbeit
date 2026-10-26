"""Geschäftslogik zum Schreiben von Filmdaten."""

from typing import Final

from loguru import logger

from film.repository import FilmRepository, Session
from film.service.exceptions import (
    DrehbuchRequiredError,
    NotFoundError,
    SchauspielerNotInFilmError,
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

    def update(self, film: Film) -> FilmDTO:
        """Aktualisiert einen Film und seine Beziehungen."""
        logger.debug("film={}", film)
        if film.id is None:
            raise NotFoundError

        if film.drehbuch is None:
            raise DrehbuchRequiredError

        with Session() as session:
            if (
                film_db := self.repo.find_by_id(film_id=film.id, session=session)
            ) is None:
                raise NotFoundError(film_id=film.id)

            film_db.titel = film.titel
            film_db.erscheinungsjahr = film.erscheinungsjahr

            drehbuch = film.drehbuch
            drehbuch_db = film_db.drehbuch
            if drehbuch.id == drehbuch_db.id:
                drehbuch_db.titel = drehbuch.titel
                drehbuch_db.autor = drehbuch.autor
                drehbuch_db.seitenzahl = drehbuch.seitenzahl
            else:
                session.delete(drehbuch_db)
                session.flush()
                drehbuch.film = None
                film_db.drehbuch = drehbuch
                session.add(drehbuch)

            schauspieler_db = {
                person.id: person
                for person in film_db.schauspieler
                if person.id is not None
            }
            schauspieler = []
            for person in list(film.schauspieler):
                if person.id in schauspieler_db:
                    person_db = schauspieler_db[person.id]
                    person_db.vorname = person.vorname
                    person_db.nachname = person.nachname
                    schauspieler.append(person_db)
                    continue
                if person.id is not None:
                    raise SchauspielerNotInFilmError(person.id)
                person.film = None
                schauspieler.append(person)
            film_db.schauspieler = schauspieler
            session.add_all(schauspieler)

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
