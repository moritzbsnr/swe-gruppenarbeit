"""Unit-Tests für create() von FilmWriteService."""

from datetime import date

import pytest

from film.entity import Film
from film.service import DrehbuchRequiredError


@pytest.mark.unit
@pytest.mark.unit_create
def test_create(
    film_write_service,
    film_repository,
    film,
    session_mock,
    mocker,
) -> None:
    mocker.patch.object(film_repository, "create", return_value=film)

    film_dto = film_write_service.create(film=film)

    assert film_dto.id == film.id
    assert film_dto.titel == film.titel
    assert film_dto.drehbuch.titel == film.drehbuch.titel
    session_mock.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.unit_create
def test_create_without_drehbuch(film_write_service) -> None:
    film = Film(
        id=None,
        titel="Mockfilm",
        erscheinungsjahr=date(2025, 1, 31),
        drehbuch=None,
        schauspieler=[],
    )

    with pytest.raises(DrehbuchRequiredError):
        film_write_service.create(film=film)
