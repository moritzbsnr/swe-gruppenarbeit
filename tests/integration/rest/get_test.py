"""Tests für das Lesen der Filmliste."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, create_film, rest_url, timeout
from requests import get


@pytest.mark.rest
@pytest.mark.get_request
def test_get_filme() -> None:
    film_id: Final = create_film()

    response: Final = get(
        f"{rest_url}/filme",
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK
    filme: Final = response.json()
    assert isinstance(filme, list)
    film: Final = next((item for item in filme if item["id"] == film_id), None)
    assert film is not None
    assert film["titel"] == "Integrationstestfilm"
    assert film["drehbuch"]["titel"] == "Integrationstests"
    assert len(film["schauspieler"]) == 1
