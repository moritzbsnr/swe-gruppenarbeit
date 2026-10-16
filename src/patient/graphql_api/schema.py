# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Schema für GraphQL durch Strawberry.

Alternative: https://github.com/graphql-python/graphene.
"""

from dataclasses import asdict
from datetime import date
from typing import Final
lazy from collections.abc import Sequence

import strawberry
from fastapi import Request
from loguru import logger
from sqlalchemy import select
from strawberry.extensions import PydanticErrorExtension
from strawberry.fastapi import GraphQLRouter
lazy from strawberry.types import Info

from patient.config.graphql import graphql_ide
from patient.entity import Drehbuch, Film, Schauspieler
from patient.graphql_api.graphql_types import (
    CreatePayload,
    FilmInput,
    LoginResult,
    PatientInput,
    Suchparameter,
)
from patient.repository import Pageable, PatientRepository, PatientSuchparameter
from patient.repository.session_factory import Session
from patient.router.patient_model import PatientModel
from patient.security import Role, TokenService, UserService
from patient.service import (
    NotFoundError,
    PatientDTO,
    PatientService,
    PatientWriteService,
)

__all__ = ["graphql_router"]


# Strawberry ist eine "code-first library":
# - keine Schema-Datei in SDL (schema definition language) notwendig
# - das Schema wird aus Klassen generiert, die mit z.B. @type oder @input dekoriert sind

# type Patient {
#     nachname: String!
# }
# input Suchparameter {...}
# type Query {
#     patient(patient_id: ID!): Patient!
#     patienten(suchparameter: Suchparameter): list[Patient!]!
# }


_repo: Final = PatientRepository()
_service: PatientService = PatientService(repo=_repo)
_user_service: UserService = UserService()
_write_service: PatientWriteService = PatientWriteService(
    repo=_repo,
    user_service=_user_service,
)
_token_service: Final = TokenService()


@strawberry.type
class SchauspielerGraphQL:
    id: int
    vorname: str
    nachname: str
    geburtsdatum: date


@strawberry.type
class DrehbuchGraphQL:
    id: int
    titel: str
    autor: str
    inhalt: str


@strawberry.type
class FilmGraphQL:
    id: int
    titel: str
    erscheinungsjahr: int
    genre: str
    schauspieler: list[SchauspielerGraphQL]
    drehbuch: DrehbuchGraphQL


@strawberry.type  # vgl. @dataclass
class Query:
    """Queries, um Patientendaten zu lesen."""

    @strawberry.field
    def patient(self, patient_id: strawberry.ID, info: Info) -> PatientDTO | None:
        """Daten zu einem Patienten lesen.

        :param patient_id: ID des gesuchten Patienten
        :return: Gesuchter Patient
        :rtype: Patient
        :raises NotFoundError: Falls kein Patient gefunden wurde, wird zu GraphQLError
        """
        logger.debug("patient_id={}", patient_id)

        request: Final[Request] = info.context.get("request")
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            patient_dto: Final = _service.find_by_id(
                patient_id=int(patient_id),
                user=user,
            )
        except NotFoundError:
            return None
        logger.debug("{}", patient_dto)
        return patient_dto

    @strawberry.field
    def patienten(
        self,
        suchparameter: Suchparameter | None,
        info: Info,
    ) -> Sequence[PatientDTO]:
        """Patienten anhand von Suchparameter suchen.

        :param suchparameter: nachname, email usw.
        :return: Die gefundenen Patienten
        :rtype: list[Patient]
        :raises NotFoundError: Falls kein Patient gefunden wurde, wird zu GraphQLError
        """
        logger.debug("suchparameter={}", suchparameter)

        request: Final[Request] = info.context["request"]
        user: Final = _token_service.get_user_from_request(request)
        if user is None or Role.ADMIN not in user.roles:
            return []

        suchparameter_filtered = (
            None
            if suchparameter is None
            else PatientSuchparameter(
                email=suchparameter.email,
                nachname=suchparameter.nachname,
            )
        )
        logger.debug("suchparameter_filtered={}", suchparameter_filtered)

        pageable: Final = Pageable.create(size=str(0))
        try:
            patienten_dto: Final = _service.find(
                suchparameter=suchparameter_filtered,
                pageable=pageable,
            )
        except NotFoundError:
            return []
        logger.debug("{}", patienten_dto)
        return patienten_dto.content

    @strawberry.field
    def filme(self) -> list[FilmGraphQL]:
        """Filme einschließlich Schauspielern und Drehbüchern lesen."""
        with Session() as session:
            filme = session.scalars(select(Film)).all()
            return [
                FilmGraphQL(
                    id=film.id if film.id is not None else -1,
                    titel=film.titel,
                    erscheinungsjahr=film.erscheinungsjahr,
                    genre=film.genre,
                    schauspieler=[
                        SchauspielerGraphQL(
                            id=actor.id if actor.id is not None else -1,
                            vorname=actor.vorname,
                            nachname=actor.nachname,
                            geburtsdatum=actor.geburtsdatum,
                        )
                        for actor in film.schauspieler
                    ],
                    drehbuch=DrehbuchGraphQL(
                        id=film.drehbuch.id if film.drehbuch.id is not None else -1,
                        titel=film.drehbuch.titel,
                        autor=film.drehbuch.autor,
                        inhalt=film.drehbuch.inhalt,
                    ),
                )
                for film in filme
            ]


@strawberry.type
class Mutation:
    """Mutations, um Patientendaten anzulegen, zu ändern oder zu löschen."""

    @strawberry.mutation
    def create(self, patient_input: PatientInput) -> CreatePayload:
        """Einen neuen Patienten anlegen.

        :param patient_input: Daten des neuen Patienten
        :return: ID des neuen Patienten
        :rtype: CreatePayload
        :raises EmailExistsError: Falls die Emailadresse bereits existiert
        :raises UsernameExistsError: Falls der Benutzername bereits existiert
        """
        logger.debug("patient_input={}", patient_input)

        # Dictonary mit Pydantic validieren
        patient_model: Final = PatientModel.model_validate(asdict(patient_input))

        patient_dto: Final = _write_service.create(patient=patient_model.to_patient())
        payload: Final = CreatePayload(id=patient_dto.id)

        logger.debug("{}", payload)
        return payload

    @strawberry.mutation
    def film_erstellen(self, film_input: FilmInput) -> int:
        """Film mit Besetzung und Drehbuch anlegen; Rückgabe ist die Film-ID."""
        film = Film(
            titel=film_input.titel,
            erscheinungsjahr=film_input.erscheinungsjahr,
            genre=film_input.genre,
            schauspieler=[
                Schauspieler(
                    vorname=actor.vorname,
                    nachname=actor.nachname,
                    geburtsdatum=actor.geburtsdatum,
                )
                for actor in film_input.schauspieler
            ],
            drehbuch=Drehbuch(
                titel=film_input.drehbuch.titel,
                autor=film_input.drehbuch.autor,
                inhalt=film_input.drehbuch.inhalt,
            ),
        )
        with Session() as session:
            session.add(film)
            session.commit()
            return film.id if film.id is not None else -1

    # Mutation, weil evtl. der Login-Zeitpunkt gespeichert wird
    @strawberry.mutation
    def login(self, username: str, password: str) -> LoginResult:
        """Einen Token zu Benutzername und Passwort ermitteln.

        :param username: Benutzername
        :param password: Passwort
        :rtype: LoginResult
        """
        logger.debug("username={}, password={}", username, password)
        token_mapping = _token_service.token(username=username, password=password)

        token = token_mapping["access_token"]
        user = _token_service.get_user_from_token(token)
        # List Comprehension ab Python 2.0 (2000) https://peps.python.org/pep-0202
        roles: Final = [role.value for role in user.roles]
        return LoginResult(token=token, expiresIn="1d", roles=roles)


schema: Final = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # https://strawberry.rocks/docs/extensions/pydantic_error_extension
    extensions=[
        PydanticErrorExtension,
    ],
)


Context = dict[str, Request]


# Dependency Injection: Request von FastAPI weiterreichen an den Kontext von Strawberry
def get_context(request: Request) -> Context:
    return {"request": request}


# https://strawberry.rocks/docs/integrations/fastapi
graphql_router: Final = GraphQLRouter[Context](
    schema,
    context_getter=get_context,
    graphql_ide=graphql_ide,
)
