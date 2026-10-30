"""Unit-Tests für find_by_id() von FilmService."""

from dataclasses import asdict

import pytest

from film.service import FilmDTO, NotFoundError


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id(
    film_service,
    film_repository,
    film,
    session_mock,
    mocker,
) -> None:
    mocker.patch.object(film_repository, "find_by_id", return_value=film)

    film_dto = film_service.find_by_id(film_id=film.id)

    assert asdict(film_dto) == asdict(FilmDTO.from_film(film))
    session_mock.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.unit_find_by_id
def test_find_by_id_not_found(
    film_service,
    film_repository,
    session_mock,
    mocker,
) -> None:
    film_id = 999
    mocker.patch.object(film_repository, "find_by_id", return_value=None)

    with pytest.raises(NotFoundError) as err:
        film_service.find_by_id(film_id=film_id)

    assert err.value.film_id == film_id
    session_mock.commit.assert_not_called()
