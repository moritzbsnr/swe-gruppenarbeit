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

"""Pydantic-Model zum partiellen Aktualisieren von Filmendaten."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

__all__ = ["FilmUpdateModel"]


class FilmUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Filmendaten."""

    # https://docs.pydantic.dev/latest/usage/types
    titel: str | None = Field(default=None, min_length=1, max_length=64)
    """Der optionale Titel."""
    erscheinungsjahr: date | None = Field(
        default=None,
        ge=date(1889, 1, 1),
        le=date(2100, 12, 31),
        strict=False,
    )
    """Das optionale Erscheinungsjahr."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "titel": "Testfilm",
                "erscheinungsjahr": "2023-01-31",
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        extra="forbid",
        frozen=True,
    )

    @model_validator(mode="after")
    def validate_changes(self) -> FilmUpdateModel:
        """Stellt sicher, dass mindestens ein nicht-leeres Feld geändert wird."""
        if not self.model_fields_set:
            raise PydanticCustomError("empty_update", "Leeres Update")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise PydanticCustomError(
                "null_update_field",
                "Nullwerte sind nicht erlaubt",
            )
        return self
