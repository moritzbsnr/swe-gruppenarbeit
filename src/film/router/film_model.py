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

"""Pydantic-Model für neue Filme."""

from datetime import date  # ruff: ignore[typing-only-standard-library-import]
from typing import Final

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from film.entity import Film
from film.router.drehbuch_model import (  # ruff: ignore[typing-only-first-party-import]
    DrehbuchModel,
)
from film.router.schauspieler_model import (  # ruff: ignore[typing-only-first-party-import]
    SchauspielerModel,
)

__all__ = ["FilmModel"]


class FilmModel(BaseModel):
    """Eingabemodell zum Anlegen eines Films mit Drehbuch und Schauspielern."""

    titel: str = Field(min_length=1, max_length=64)
    erscheinungsjahr: date = Field(strict=False)
    drehbuch: DrehbuchModel
    schauspieler: list[SchauspielerModel] = Field(min_length=1)

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    def to_film(self) -> Film:
        """Konvertiert die Eingabedaten in eine Film-Entity."""
        logger.debug("self={}", self)
        film: Final = Film(
            id=None,
            titel=self.titel,
            erscheinungsjahr=self.erscheinungsjahr,
            drehbuch=self.drehbuch.to_drehbuch(),
            schauspieler=[
                actor.to_schauspieler() for actor in self.schauspieler
            ],
        )
        logger.debug("film={}", film)
        return film
