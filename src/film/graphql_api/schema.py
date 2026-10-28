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

from typing import Final
lazy from datetime import date

import strawberry
from fastapi import Request
from loguru import logger
from strawberry.extensions import PydanticErrorExtension
from strawberry.fastapi import GraphQLRouter
lazy from strawberry.types import Info

from film.config.graphql import graphql_ide
from film.entity import Drehbuch, Film, Schauspieler
from film.graphql_api.graphql_types import (
    CreatePayload,
    FilmInput,
    LoginResult,
)
from film.repository import FilmRepository, Pageable, Session
from film.security import TokenService
from film.service import (
    FilmService,
    FilmWriteService,
    NotFoundError,
)

__all__ = ["Mutation", "Query", "graphql_router"]


# Strawberry ist eine "code-first library":
# - keine Schema-Datei in SDL (schema definition language) notwendig
# - das Schema wird aus Klassen generiert, die mit z.B. @type oder @input dekoriert sind

_repo: Final = FilmRepository()
_service: FilmService = FilmService(repo=_repo)
_write_service: FilmWriteService = FilmWriteService(repo=_repo)
_token_service: Final = TokenService()


@strawberry.type
class SchauspielerGraphQL:
    id: int
    vorname: str
    nachname: str


@strawberry.type
class DrehbuchGraphQL:
    id: int
    titel: str
    autor: str
    seitenzahl: int


@strawberry.type
class FilmGraphQL:
    id: int
    titel: str
    erscheinungsjahr: date
    schauspieler: list[SchauspielerGraphQL]
    drehbuch: DrehbuchGraphQL


@strawberry.type  # vgl. @dataclass
class Query:
    """Queries, um Filmendaten zu lesen."""

    @strawberry.field
    def film(self, film_id: strawberry.ID, info: Info) -> FilmGraphQL | None:
        """Daten zu einem Film lesen.

        :param film_id: ID des gesuchten Films
        :return: Gesuchter Film
        :rtype: FilmGraphQL
        :raises NotFoundError: Falls kein Film gefunden wurde
        """
        logger.debug("film_id={}", film_id)

        request: Final[Request] = info.context["request"]
        user: Final = _token_service.get_user_from_request(request=request)
        if user is None:
            return None

        try:
            film_dto: Final = _service.find_by_id(film_id=int(film_id))
        except NotFoundError:
            return None
        logger.debug("{}", film_dto)
        return FilmGraphQL(
            id=film_dto.id,
            titel=film_dto.titel,
            erscheinungsjahr=film_dto.erscheinungsjahr,
            schauspieler=[
                SchauspielerGraphQL(
                    id=actor.id,
                    vorname=actor.vorname,
                    nachname=actor.nachname,
                )
                for actor in film_dto.schauspieler
            ],
            drehbuch=DrehbuchGraphQL(
                id=film_dto.drehbuch.id,
                titel=film_dto.drehbuch.titel,
                autor=film_dto.drehbuch.autor,
                seitenzahl=film_dto.drehbuch.seitenzahl,
            ),
        )

    @strawberry.field
    def filme(self) -> list[FilmGraphQL]:
        """Filme einschließlich Schauspielern und Drehbüchern lesen."""
        pageable: Final = Pageable.create(size="0")
        with Session() as session:
            filme = _repo.find_all(pageable=pageable, session=session).content
            return [
                FilmGraphQL(
                    id=film.id if film.id is not None else -1,
                    titel=film.titel,
                    erscheinungsjahr=film.erscheinungsjahr,
                    schauspieler=[
                        SchauspielerGraphQL(
                            id=actor.id if actor.id is not None else -1,
                            vorname=actor.vorname,
                            nachname=actor.nachname,
                        )
                        for actor in film.schauspieler
                    ],
                    drehbuch=DrehbuchGraphQL(
                        id=film.drehbuch.id if film.drehbuch.id is not None else -1,
                        titel=film.drehbuch.titel,
                        autor=film.drehbuch.autor,
                        seitenzahl=film.drehbuch.seitenzahl,
                    ),
                )
                for film in filme
            ]


@strawberry.type
class Mutation:
    """Mutations zum Erstellen von Filmen und Einloggen."""

    @strawberry.mutation
    def create(self, film_input: FilmInput) -> CreatePayload:
        """Einen neuen Film anlegen.

        :param film_input: Daten des neuen Films
        :return: ID des neuen Films
        :rtype: CreatePayload
        """
        logger.debug("film_input={}", film_input)

        film = Film(
            id=None,
            titel=film_input.titel,
            erscheinungsjahr=film_input.erscheinungsjahr,
            schauspieler=[
                Schauspieler(
                    id=None,
                    vorname=actor.vorname,
                    nachname=actor.nachname,
                    film=None,
                )
                for actor in film_input.schauspieler
            ],
            drehbuch=Drehbuch(
                id=None,
                titel=film_input.drehbuch.titel,
                autor=film_input.drehbuch.autor,
                seitenzahl=film_input.drehbuch.seitenzahl,
                film=None,
            ),
        )
        film_dto: Final = _write_service.create(film=film)
        payload: Final = CreatePayload(id=film_dto.id)

        logger.debug("{}", payload)
        return payload

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
