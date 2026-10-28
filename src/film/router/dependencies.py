# Copyright (C) 2025 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Factory-Funktionen für Dependency Injection."""

from typing import Annotated

from fastapi import Depends

from film.repository.film_repository import FilmRepository
from film.service.film_service import FilmService
from film.service.film_write_service import FilmWriteService


def get_repository() -> FilmRepository:
    """Factory-Funktion für FilmRepository.

    :return: Das Repository
    :rtype: FilmRepository
    """
    return FilmRepository()


def get_service(
    repo: Annotated[FilmRepository, Depends(get_repository)],
) -> FilmService:
    """Factory-Funktion für FilmService."""
    return FilmService(repo=repo)


def get_write_service(
    repo: Annotated[FilmRepository, Depends(get_repository)],
) -> FilmWriteService:
    """Factory-Funktion für FilmWriteService."""
    return FilmWriteService(repo=repo)
