"""Modul für persistente Patientendaten."""

from film.entity.adresse import Adresse
from film.entity.base import Base
from film.entity.drehbuch import Drehbuch
from film.entity.facharzt import Facharzt
from film.entity.film import Film
from film.entity.familienstand import Familienstand
from film.entity.geschlecht import Geschlecht
from film.entity.patient import Patient
from film.entity.rechnung import Rechnung
from film.entity.schauspieler import Schauspieler

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "Adresse",
    "Base",
    "Drehbuch",
    "Facharzt",
    "Film",
    "Familienstand",
    "Geschlecht",
    "Patient",
    "Rechnung",
    "Schauspieler",
]
