# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""DTO-Klasse für Patientendaten, insbesondere ohne Decorators für SQLAlchemy."""

from dataclasses import dataclass
lazy from datetime import date

import strawberry

from film.entity import Facharzt, Familienstand, Geschlecht, Patient
from film.service.adresse_dto import AdresseDTO

__all__ = ["PatientDTO"]


# Mit der Funktion asdict() kann ein Objekt einfach in ein dict konvertiert werden
# init=True (default): __init__ fuer die "member variables" wird generiert
# eq=True (default): __eq__ wird generiert
# unsafe_hash=False (default): __hash__ passend zu __eq__ wird generiert
# repr=True (default): __repr__ wird generiert
# frozen=False (default): mutable
# kw_only=False (default): Initialisierungs-Fkt auch ohne "Keyword Arguments" aufrufen
# slots=False (default): __dict__ zur Speicherung statt slots
# slots: schnellerer Zugriff, kompakte Speicherung
# https://stackoverflow.com/questions/472000/usage-of-slots
@dataclass(eq=False, slots=True, kw_only=True)
# Strawberry konvertiert automatisch zwischen snake_case (Python) und camelCase (Schema)
@strawberry.type(name="Patient")
class PatientDTO:
    """DTO-Klasse für aus gelesene oder gespeicherte Patientendaten: ohne Decorators."""

    id: int
    version: int
    nachname: str
    email: str
    kategorie: int
    has_newsletter: bool
    # https://docs.python.org/3/library/datetime.html
    geburtsdatum: date
    homepage: str | None
    geschlecht: Geschlecht | None
    familienstand: Familienstand | None
    adresse: AdresseDTO
    fachaerzte: list[Facharzt]
    username: str | None

    # asdict kann nicht verwendet werden: Rueckwaertsverweise Patient - Adresse
    # https://github.com/python/cpython/issues/94345
    @classmethod
    def from_patient(cls, patient: Patient) -> PatientDTO:
        """Initialisierung von PatientDTO durch ein Entity-Objekt von Patient.

        :param patient: Patient-Objekt mit Decorators zu SQLAlchemy
        :return: PatientDTO-Objekt mit Daten aus dem Patient-Objekt
        :rtype: PatientDTO
        """
        return cls(
            id=film.id if film.id is not None else -1,
            version=film.version,
            nachname=film.nachname,
            email=film.email,
            kategorie=film.kategorie,
            has_newsletter=film.has_newsletter,
            geburtsdatum=film.geburtsdatum,
            homepage=film.homepage,
            geschlecht=film.geschlecht,
            familienstand=film.familienstand,
            adresse=AdresseDTO.from_adresse(film.adresse),
            fachaerzte=(
                [Facharzt[facharzt] for facharzt in film.fachaerzte_json]
                if film.fachaerzte_json is not None
                else []
            ),
            username=film.username if film.username is not None else "N/A",
        )
