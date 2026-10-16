"""Modul für persistente Patientendaten."""

from patient.entity.adresse import Adresse
from patient.entity.base import Base
from patient.entity.drehbuch import Drehbuch
from patient.entity.facharzt import Facharzt
from patient.entity.film import Film
from patient.entity.familienstand import Familienstand
from patient.entity.geschlecht import Geschlecht
from patient.entity.patient import Patient
from patient.entity.rechnung import Rechnung
from patient.entity.schauspieler import Schauspieler

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
