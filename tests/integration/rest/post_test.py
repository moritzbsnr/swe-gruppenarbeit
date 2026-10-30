"""Tests für das Anlegen eines Films."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, create_film, rest_url, timeout
from requests import post


@pytest.mark.rest
@pytest.mark.post_request
def test_post() -> None:
    film_id: Final = create_film()

    response: Final = post(
        f"{rest_url}/filme/{film_id}",
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.rest
@pytest.mark.post_request
def test_post_invalid() -> None:
    response: Final = post(
        rest_url,
        json={"titel": "", "erscheinungsjahr": "kein-datum"},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.rest
@pytest.mark.post_request
def test_post_invalid_json() -> None:
    response: Final = post(
        rest_url,
        data='{"titel" "Film"}',
        headers={"Content-Type": "application/json"},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
