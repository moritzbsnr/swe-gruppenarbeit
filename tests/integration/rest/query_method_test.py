"""Tests für nicht unterstützte HTTP-Methoden der Filmressource."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, rest_url, timeout
from requests import request


@pytest.mark.rest
@pytest.mark.query_request
def test_query_method_not_allowed() -> None:
    response: Final = request(
        method="QUERY",
        url=f"{rest_url}/filme",
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
