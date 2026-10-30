"""Tests für das Aktualisieren eines Films."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import (
    certificate_path,
    create_film,
    login,
    rest_url,
    timeout,
)
from requests import get, put


@pytest.mark.rest
@pytest.mark.put_request
def test_put() -> None:
    film_id: Final = create_film()
    token: Final = login()
    response: Final = put(
        f"{rest_url}/{film_id}",
        json={"titel": "Aktualisierter Film"},
        headers={"Authorization": f"Bearer {token}", "If-Match": '"0"'},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text

    updated: Final = get(
        f"{rest_url}/filme/{film_id}",
        timeout=timeout,
        verify=certificate_path,
    )
    assert updated.status_code == HTTPStatus.OK
    assert updated.json()["titel"] == "Aktualisierter Film"


@pytest.mark.rest
@pytest.mark.put_request
def test_put_invalid() -> None:
    film_id: Final = create_film()
    token: Final = login()
    response: Final = put(
        f"{rest_url}/{film_id}",
        json={"titel": ""},
        headers={"Authorization": f"Bearer {token}", "If-Match": '"0"'},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.rest
@pytest.mark.put_request
def test_put_not_found() -> None:
    token: Final = login()
    response: Final = put(
        f"{rest_url}/999999999",
        json={"titel": "Nicht vorhanden"},
        headers={"Authorization": f"Bearer {token}", "If-Match": '"0"'},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.put_request
def test_put_without_if_match() -> None:
    film_id: Final = create_film()
    token: Final = login()
    response: Final = put(
        f"{rest_url}/{film_id}",
        json={"titel": "Aktualisierter Film"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@pytest.mark.rest
@pytest.mark.put_request
@pytest.mark.parametrize("if_match", ['"xy', "0"])
def test_put_invalid_if_match(if_match: str) -> None:
    film_id: Final = create_film()
    token: Final = login()
    response: Final = put(
        f"{rest_url}/{film_id}",
        json={"titel": "Aktualisierter Film"},
        headers={"Authorization": f"Bearer {token}", "If-Match": if_match},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
