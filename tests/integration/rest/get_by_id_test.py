"""Tests für das Lesen eines Films anhand seiner ID."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, create_film, rest_url, timeout
from requests import get


@pytest.mark.rest
@pytest.mark.get_request
def test_get_by_id() -> None:
    film_id: Final = create_film()

    response: Final = get(
        f"{rest_url}/filme/{film_id}",
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK
    film: Final = response.json()
    assert film["id"] == film_id
    assert film["titel"] == "Integrationstestfilm"
    assert film["drehbuch"]["autor"] == "Testautor"
    assert film["schauspieler"][0]["nachname"] == "Darsteller"


@pytest.mark.rest
@pytest.mark.get_request
def test_get_by_id_not_found() -> None:
    response: Final = get(
        f"{rest_url}/filme/999999999",
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
