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

"""Pydantic-Model für die Adresse."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from film.entity import Drehbuch

__all__ = ["DrehbuchModel"]


class DrehbuchModel(BaseModel):
    """Pydantic-Model für das Drehbuch."""

    titel: Annotated[str, StringConstraints(max_length=128)]
    """Titel des Drehbuchs"""
    autor: Annotated[str, StringConstraints(max_length=128)]
    """Autor des Drehbuchs"""
    seitenzahl: Annotated[int, Field(gt=0)]
    """Seitenzahl des Drehbuchs"""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "titel": "Testtitel",
                "autor": "Testautor",
                "seitenzahl": 100,
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_drehbuch(self) -> Drehbuch:
        """Konvertierung in ein Drehbuch-Objekt für SQLAlchemy.

        :return: Drehbuch-Objekt für SQLAlchemy
        :rtype: Drehbuch
        """
        return Drehbuch(
            id=None,
            titel=self.titel,
            autor=self.autor,
            seitenzahl=self.seitenzahl,
            film=None,
        )
