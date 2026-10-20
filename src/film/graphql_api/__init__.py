"""Modul für die GraphQL-Schnittstelle."""

from film.graphql_api.graphql_types import (
    AdresseInput,
    CreatePayload,
    PatientInput,
    RechnungInput,
    Suchparameter,
)
from film.graphql_api.schema import Mutation, Query, graphql_router

__all__ = [
    "AdresseInput",
    "CreatePayload",
    "Mutation",
    "PatientInput",
    "Query",
    "RechnungInput",
    "Suchparameter",
    "graphql_router",
]
