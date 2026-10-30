"""Unit-Tests für find() von FilmService."""

import pytest

from film.repository import FilmSuchparameter, Pageable, Slice
from film.service import NotFoundError


@pytest.mark.unit
@pytest.mark.unit_find
def test_find_by_titel(
    film_service,
    film_repository,
    film,
    session_mock,
    mocker,
) -> None:
    suchparameter = FilmSuchparameter(titel=film.titel)
    pageable = Pageable(size=5, number=0)
    mocker.patch.object(
        film_repository,
        "find",
        return_value=Slice(content=(film,), total_elements=1),
    )

    film_slice = film_service.find(suchparameter=suchparameter, pageable=pageable)

    assert len(film_slice.content) == 1
    assert film_slice.content[0].titel == film.titel
    assert film_slice.total_elements == 1
    session_mock.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.unit_find
def test_find_not_found(
    film_service,
    film_repository,
    session_mock,
    mocker,
) -> None:
    suchparameter = FilmSuchparameter(titel="Notfound")
    pageable = Pageable(size=5, number=0)
    mocker.patch.object(
        film_repository,
        "find",
        return_value=Slice(content=(), total_elements=0),
    )

    with pytest.raises(NotFoundError) as err:
        film_service.find(suchparameter=suchparameter, pageable=pageable)

    assert err.value.suchparameter == suchparameter
    session_mock.commit.assert_not_called()
