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

"""Schema für GraphQL."""

lazy from datetime import date

import strawberry

__all__ = [
    "CreatePayload",
    "DrehbuchInput",
    "FilmInput",
    "SchauspielerInput",
    "Suchparameter",
]


@strawberry.input
class Suchparameter:
    """Suchparameter für die Suche nach Filmen."""

    nachname: str | None = None
    """Nachname als Suchkriterium."""

    email: str | None = None
    """Emailadresse als Suchkriterium."""


@strawberry.input
class DrehbuchInput:
    """Drehbuchangaben für einen Film."""

    titel: str
    """Titel des Drehbuchs."""

    autor: str
    """Autor des Drehbuchs."""

    seitenzahl: int
    """Seitentahl des Drehbuchs."""


@strawberry.input
class SchauspielerInput:
    """Schauspielerangaben für einen Film."""

    vorname: str
    """Vorname des Schauspielers."""

    nachname: str
    """Nachname des Schauspielers."""


@strawberry.input
class FilmInput:
    """Daten für einen neuen Film."""

    titel: str
    """Titel des Films."""

    erscheinungsjahr: date
    """Erscheinungsjahr des Films."""

    schauspieler: list[SchauspielerInput]
    """Schauspieler des Films."""

    drehbuch: DrehbuchInput
    """Drehbuch des Films."""


@strawberry.type
class CreatePayload:
    """Resultat-Typ, wenn ein neuer Film angelegt wurde."""

    id: int
    """ID des neu angelegten Films"""


@strawberry.type
class LoginResult:
    """Resultat-Typ, wenn ein Login erfolgreich war."""

    token: str
    """Token des eingeloggten Users."""
    expiresIn: str  # ruff: ignore[mixed-case-variable-in-class-scope]  # NOSONAR
    """Gültigkeitsdauer des Tokens."""
    roles: list[str]
    """Rollen des eingeloggten Users."""
