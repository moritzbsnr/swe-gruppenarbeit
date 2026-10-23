"""Modul für persistente Patientendaten."""

from film.entity.base import Base
from film.entity.drehbuch import Drehbuch
from film.entity.film import Film
from film.entity.schauspieler import Schauspieler

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "Base",
    "Drehbuch",
    "Film",
    "Schauspieler",
]
