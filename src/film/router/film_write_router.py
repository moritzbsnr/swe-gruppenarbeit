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

"""FilmWriteRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from loguru import logger

from film.problem_details import ProblemDetails
from film.router.constants import IF_MATCH, IF_MATCH_MIN_LEN
from film.router.dependencies import get_write_service
from film.security import Role, RolesRequired
from film.service import send_mail
lazy from film.router.film_model import FilmModel
lazy from film.router.film_update_model import FilmUpdateModel
lazy from film.service import FilmWriteService

__all__ = ["film_write_router"]


film_write_router: Final = APIRouter(tags=["Schreiben"])


@film_write_router.post("")
def post(
    film_model: FilmModel,
    request: Request,
    background_tasks: BackgroundTasks,
    service: Annotated[FilmWriteService, Depends(get_write_service)],
) -> Response:
    """POST-Request, um einen neuen Film anzulegen.

    :param film_model: Filmendaten als Pydantic-Model
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit der Request-URL
    :param background_tasks: Hintergrundtask für den Mailversand
    :param service: Injizierter Service für Geschäftslogik
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die Emailadresse bereits existiert
    :raises UsernameExistsError: Falls der Benutzername bereits existiert
    """
    logger.debug("film_model={}", film_model)
    film_dto: Final = service.create(
        film=film_model.to_film(),
    )
    logger.debug("film_dto={}", film_dto)

    background_tasks.add_task(send_mail, film_dto)

    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"{request.url}/{film_dto.id}"},
        background=background_tasks,
    )


@film_write_router.put(
    "/{film_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.FILM]))],
)
def put(
    film_id: int,
    film_update_model: FilmUpdateModel,
    request: Request,
    service: Annotated[FilmWriteService, Depends(get_write_service)],
) -> Response:
    """PUT-Request, um einen Film zu aktualisieren.

    :param film_id: ID des zu aktualisierenden Films als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit If-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    :raises ValidationError: Falls es bei Pydantic Validierungsfehler gibt
    :raises EmailExistsError: Falls die neue Emailadresse bereits
    :raises NotFoundError: Falls zur id kein Patient existiert
    :raises VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
    """
    if_match_value: Final = request.headers.get(IF_MATCH)
    logger.debug(
        "film_id={}, if_match={}, film_update_model={}",
        film_id,
        if_match_value,
        film_update_model,
    )

    if if_match_value is None:
        return ProblemDetails.create(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
        ).to_response()

    if (
        len(if_match_value) < IF_MATCH_MIN_LEN
        or not if_match_value.startswith('"')
        or not if_match_value.endswith('"')
    ):
        return ProblemDetails.create(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
        ).to_response()

    film_modified: Final = service.update(
        film_id=film_id,
        titel=film_update_model.titel,
        erscheinungsjahr=film_update_model.erscheinungsjahr,
    )
    logger.debug("film_modified={}", film_modified)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
        headers={"ETag": f'"{film_modified}"'},
    )


@film_write_router.delete(
    "/{film_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.FILM]))],
)
def delete_by_id(
    film_id: int,
    service: Annotated[FilmWriteService, Depends(get_write_service)],
) -> Response:
    """DELETE-Request, um einen Film anhand seiner ID zu löschen.

    :param film_id: ID des zu löschenden Films
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 204
    :rtype: Response
    """
    logger.debug("film_id={}", film_id)
    service.delete_by_id(film_id=film_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
