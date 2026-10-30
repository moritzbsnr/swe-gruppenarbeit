"""Tests für GraphQL-Queries zu Filmen."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import (
    certificate_path,
    create_film,
    graphql_url,
    login_graphql,
    timeout,
)
from requests import post


@pytest.mark.graphql
@pytest.mark.query
def test_query_film() -> None:
    film_id: Final = create_film()
    token: Final = login_graphql()
    query: Final = {
        "query": f"""
            {{
                film(filmId: "{film_id}") {{
                    id
                    titel
                    drehbuch {{ titel autor seitenzahl }}
                    schauspieler {{ vorname nachname }}
                }}
            }}
        """,
    }

    response: Final = post(
        graphql_url,
        json=query,
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK
    body: Final = response.json()
    assert body.get("errors") is None
    film: Final = body["data"]["film"]
    assert film["id"] == film_id
    assert film["titel"] == "Integrationstestfilm"
    assert film["drehbuch"]["autor"] == "Testautor"
    assert film["schauspieler"][0]["nachname"] == "Darsteller"


@pytest.mark.graphql
@pytest.mark.query
def test_query_film_not_found() -> None:
    token: Final = login_graphql()
    response: Final = post(
        graphql_url,
        json={"query": '{ film(filmId: "999999999") { id titel } }'},
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK
    body: Final = response.json()
    assert body.get("errors") is None
    assert body["data"]["film"] is None


@pytest.mark.graphql
@pytest.mark.query
def test_query_filme() -> None:
    film_id: Final = create_film()
    response: Final = post(
        graphql_url,
        json={"query": "{ filme { id titel } }"},
        timeout=timeout,
        verify=certificate_path,
    )

    assert response.status_code == HTTPStatus.OK
    body: Final = response.json()
    assert body.get("errors") is None
    filme: Final = body["data"]["filme"]
    assert any(film["id"] == film_id for film in filme)
