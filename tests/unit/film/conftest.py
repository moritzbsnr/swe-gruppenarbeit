"""Gemeinsame Fixtures für die Film-Unit-Tests."""

from datetime import date
from typing import TYPE_CHECKING

import pytest

from film.entity import Drehbuch, Film
from film.repository import FilmRepository
from film.service import FilmService, FilmWriteService

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def film_repository() -> FilmRepository:
    """Erzeugt ein Film-Repository."""
    return FilmRepository()


@pytest.fixture
def film_service(film_repository: FilmRepository) -> FilmService:
    """Erzeugt den Film-Lese-Service."""
    return FilmService(film_repository)


@pytest.fixture
def film_write_service(film_repository: FilmRepository) -> FilmWriteService:
    """Erzeugt den Film-Schreib-Service."""
    return FilmWriteService(film_repository)


@pytest.fixture
def film() -> Film:
    """Erzeugt einen Film mit dem erforderlichen Drehbuch."""
    return Film(
        id=1,
        titel="Mockfilm",
        erscheinungsjahr=date(2025, 1, 31),
        drehbuch=Drehbuch(
            id=1,
            titel="Mockdrehbuch",
            autor="Mockautor",
            seitenzahl=100,
        ),
        schauspieler=[],
    )


@pytest.fixture
def session_mock(mocker: MockerFixture):
    """Ersetzt die SQLAlchemy-Session in den Services."""
    session = mocker.Mock()
    session_context = mocker.MagicMock()
    session_context.__enter__.return_value = session
    mocker.patch("film.service.film_service.Session", return_value=session_context)
    mocker.patch(
        "film.service.film_write_service.Session",
        return_value=session_context,
    )
    return session
