"""Tests für GraphQL-Mutationen zu Filmen."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, graphql_url, timeout
from requests import post


@pytest.mark.graphql
@pytest.mark.mutation
def test_create() -> None:
    query: Final = {
        "query": """
            mutation {
                create(
                    filmInput: {
                        titel: "GraphQL Integrationstestfilm"
                        erscheinungsjahr: "2024-01-31"
                        schauspieler: [{ vorname: "Test", nachname: "Darsteller" }]
                        drehbuch: {
                            titel: "GraphQL Drehbuch"
                            autor: "Testautor"
                            seitenzahl: 42
                        }
                    }
                ) {
                    id
                }
            }
        """,
    }

    response: Final = post(
        graphql_url,
        json=query,
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK
    body: Final = response.json()
    assert body.get("errors") is None
    assert isinstance(body["data"]["create"]["id"], int)


@pytest.mark.graphql
@pytest.mark.mutation
def test_create_invalid() -> None:
    query: Final = {
        "query": """
            mutation {
                create(
                    filmInput: {
                        titel: "Ungültiger Film"
                        erscheinungsjahr: "kein-datum"
                        schauspieler: [{ vorname: "Test", nachname: "Darsteller" }]
                        drehbuch: {
                            titel: "Ungültig"
                            autor: "Testautor"
                            seitenzahl: 42
                        }
                    }
                ) {
                    id
                }
            }
        """,
    }

    response: Final = post(
        graphql_url,
        json=query,
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK
    body: Final = response.json()
    assert body["data"] is None
    assert isinstance(body["errors"], list)
    assert body["errors"]
