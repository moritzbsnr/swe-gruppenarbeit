"""Modul für den DB-Zugriff."""

from film.repository.film_repository import FilmRepository
from film.repository.film_suchparameter import FilmSuchparameter
from film.repository.pageable import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    Pageable,
)
from film.repository.session_factory import Session, engine
from film.repository.slice import Slice

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "DEFAULT_PAGE_NUMBER",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "FilmRepository",
    "FilmSuchparameter",
    "Pageable",
    "Session",
    "Slice",
    "engine",
]
