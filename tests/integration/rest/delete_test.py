"""Tests für das Löschen eines Films."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, create_film, login, rest_url, timeout
from requests import delete, get


@pytest.mark.rest
@pytest.mark.delete_request
def test_delete() -> None:
    film_id: Final = create_film()
    token: Final = login()
    response: Final = delete(
        f"{rest_url}/{film_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    deleted: Final = get(
        f"{rest_url}/filme/{film_id}",
        timeout=timeout,
        verify=certificate_path,
    )
    assert deleted.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.delete_request
def test_delete_not_found() -> None:
    token: Final = login()
    response: Final = delete(
        f"{rest_url}/999999999",
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
