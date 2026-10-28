"""Modul für den Geschäftslogik."""

from film.service.exceptions import (
    DrehbuchRequiredError,
    EmailExistsError,
    ForbiddenError,
    NotFoundError,
    SchauspielerNotInFilmError,
    UsernameExistsError,
    VersionOutdatedError,
)
from film.service.film_dto import DrehbuchDTO, FilmDTO, SchauspielerDTO
from film.service.film_service import FilmService
from film.service.film_write_service import FilmWriteService
from film.service.mailer import send_mail

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "DrehbuchDTO",
    "DrehbuchRequiredError",
    "EmailExistsError",
    "FilmDTO",
    "FilmService",
    "FilmWriteService",
    "ForbiddenError",
    "NotFoundError",
    "SchauspielerDTO",
    "SchauspielerNotInFilmError",
    "UsernameExistsError",
    "VersionOutdatedError",
    "send_mail"
]
