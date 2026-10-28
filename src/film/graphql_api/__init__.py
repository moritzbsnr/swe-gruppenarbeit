"""Modul für die GraphQL-Schnittstelle."""

from film.graphql_api.graphql_types import (
    CreatePayload,
    DrehbuchInput,
    FilmInput,
    SchauspielerInput,
    Suchparameter,
)
from film.graphql_api.schema import Mutation, Query, graphql_router

__all__ = [
    "CreatePayload",
    "DrehbuchInput",
    "FilmInput",
    "Mutation",
    "Query",
    "SchauspielerInput",
    "Suchparameter",
    "graphql_router",
]
