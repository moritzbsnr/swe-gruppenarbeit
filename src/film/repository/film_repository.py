"""Repository für persistente Filmdaten."""

from typing import Final
lazy from collections.abc import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload
lazy from sqlalchemy.sql import Select
lazy from sqlalchemy.sql.elements import ColumnElement

from film.entity import Film
from film.repository.slice import Slice
lazy from film.repository.film_suchparameter import FilmSuchparameter
lazy from film.repository.pageable import Pageable

__all__ = ["FilmRepository"]


class FilmRepository:
    """Repository-Klasse mit CRUD-Methoden für die Entity-Klasse Film."""

    @staticmethod
    def _with_relationships(
        statement: Select[Film],
    ) -> Select[Film]:
        return statement.options(
            joinedload(Film.drehbuch),
            selectinload(Film.schauspieler),
        )

    def find_by_id(self, film_id: int | None, session: Session) -> Film | None:
        """Suche einen Film anhand seiner ID."""
        logger.debug("film_id={}", film_id)

        if film_id is None:
            return None

        statement: Final = self._with_relationships(
            select(Film).where(Film.id == film_id),
        )
        film = session.scalar(statement)
        logger.debug("{}", film)
        return film

    def find(
        self,
        suchparameter: FilmSuchparameter | None,
        pageable: Pageable,
        session: Session,
    ) -> Slice[Film]:
        """Suche Filme nach Titel und/oder Erscheinungsjahr."""
        logger.debug("suchparameter={}", suchparameter)
        if suchparameter is None or suchparameter.is_empty():
            return self._find_all(pageable=pageable, session=session)

        filters = self._filters(suchparameter)
        offset = pageable.number * pageable.size
        statement = self._with_relationships(
            select(Film).where(*filters),
        )
        if pageable.size != 0:
            statement = statement.limit(pageable.size).offset(offset)

        films = session.scalars(statement).all()
        count_statement: Final = (
            select(func.count()).select_from(Film).where(*filters)
        )
        count = session.scalar(count_statement)
        result = Slice(
            content=tuple(films),
            total_elements=count if count is not None else 0,
        )
        logger.debug("film_slice={}", result)
        return result

    def find_all(self, pageable: Pageable, session: Session) -> Slice[Film]:
        """Suche Filme mit Pagination inklusive Drehbuch und Schauspielern."""
        return self._find_all(pageable=pageable, session=session)

    def _find_all(self, pageable: Pageable, session: Session) -> Slice[Film]:
        offset = pageable.number * pageable.size
        statement = self._with_relationships(select(Film))
        if pageable.size != 0:
            statement = statement.limit(pageable.size).offset(offset)

        films = session.scalars(statement).all()
        count_statement: Final = select(func.count()).select_from(Film)
        count = session.scalar(count_statement)
        result = Slice(
            content=tuple(films),
            total_elements=count if count is not None else 0,
        )
        logger.debug("film_slice={}", result)
        return result

    @staticmethod
    def _filters(
        suchparameter: FilmSuchparameter,
    ) -> tuple[ColumnElement[bool], ...]:
        filters: list[ColumnElement[bool]] = []
        if suchparameter.titel is not None:
            filters.append(Film.titel.ilike(f"%{suchparameter.titel}%"))
        if suchparameter.erscheinungsjahr is not None:
            filters.append(Film.erscheinungsjahr == suchparameter.erscheinungsjahr)
        return tuple(filters)

    def exists_titel(self, titel: str, session: Session) -> bool:
        """Prüft, ob ein Film mit exakt diesem Titel existiert."""
        statement: Final = select(func.count()).where(Film.titel == titel)
        count = session.scalar(statement)
        return count is not None and count > 0

    def create(self, film: Film, session: Session) -> Film:
        """Speichere einen Film samt Drehbuch und Schauspielern."""
        logger.debug("film={}", film)
        session.add(instance=film)
        session.flush(objects=[film])
        logger.debug("film_id={}", film.id)
        return film

    def update(self, film: Film, session: Session) -> Film | None:
        """Aktualisiere einen Film und seine Beziehungen."""
        logger.debug("{}", film)

        if (film_db := self.find_by_id(film_id=film.id, session=session)) is None:
            return None

        film_db.titel = film.titel
        film_db.erscheinungsjahr = film.erscheinungsjahr
        film_db.drehbuch = film.drehbuch
        film_db.schauspieler = film.schauspieler
        logger.debug("{}", film_db)
        return film_db

    def delete_by_id(self, film_id: int, session: Session) -> None:
        """Lösche einen Film samt zugehörigem Drehbuch und Schauspielern."""
        logger.debug("film_id={}", film_id)

        if (film := self.find_by_id(film_id=film_id, session=session)) is None:
            return

        session.delete(film)
        logger.debug("ok")

    def find_titel(self, teil: str, session: Session) -> Sequence[str]:
        """Suche eindeutige Filmtitel, die den angegebenen Teil enthalten."""
        logger.debug("teil={}", teil)
        statement: Final = (
            select(Film.titel)
            .where(Film.titel.ilike(f"%{teil}%"))
            .distinct()
        )
        titel: Final = session.scalars(statement).all()
        logger.debug("titel={}", titel)
        return titel
