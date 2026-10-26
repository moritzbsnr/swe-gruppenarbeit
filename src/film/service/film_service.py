"""Geschäftslogik zum Lesen von Filmdaten."""

from typing import Final
lazy from collections.abc import Sequence

from loguru import logger

from film.repository import (
    FilmRepository,
    FilmSuchparameter,
    Pageable,
    Session,
    Slice,
)
from film.service.exceptions import NotFoundError
from film.service.film_dto import FilmDTO

__all__ = ["FilmService"]


class FilmService:
    """Service zum Suchen und Lesen von Filmen."""

    def __init__(self, repo: FilmRepository) -> None:
        """Initialisiert den Service mit dem Film-Repository."""
        self.repo = repo

    def find_by_id(self, film_id: int) -> FilmDTO:
        """Liefert einen Film mit Drehbuch und Schauspielern anhand seiner ID."""
        logger.debug("film_id={}", film_id)
        with Session() as session:
            film = self.repo.find_by_id(film_id=film_id, session=session)
            if film is None:
                raise NotFoundError(film_id=film_id)

            film_dto: Final = FilmDTO.from_film(film)
            session.commit()

        return film_dto

    def find(
        self,
        suchparameter: FilmSuchparameter | None,
        pageable: Pageable,
    ) -> Slice[FilmDTO]:
        """Sucht Filme mit Pagination und wandelt deren Beziehungen in DTOs um."""
        logger.debug("suchparameter={}", suchparameter)
        with Session() as session:
            film_slice = self.repo.find(
                suchparameter=suchparameter,
                pageable=pageable,
                session=session,
            )
            if not film_slice.content:
                raise NotFoundError(suchparameter=suchparameter)

            filme_dto: Final = tuple(
                FilmDTO.from_film(film) for film in film_slice.content
            )
            session.commit()

        return Slice(
            content=filme_dto,
            total_elements=film_slice.total_elements,
        )

    def find_titel(self, teil: str) -> Sequence[str]:
        """Liefert eindeutige Filmtitel, die den Suchtext enthalten."""
        with Session() as session:
            titel: Final = self.repo.find_titel(teil=teil, session=session)
            session.commit()

        if not titel:
            raise NotFoundError
        return titel
