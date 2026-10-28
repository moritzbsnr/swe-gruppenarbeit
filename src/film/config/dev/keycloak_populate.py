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

"""Neuladen von Keycloak im Modus DEV."""

from csv import DictReader
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from keycloak import KeycloakConnectionError
from loguru import logger

from film.config import csv_config
from film.config.dev_modus import dev_keycloak_populate
from film.security import User, UserService
from film.security.dependencies import get_user_service
from film.security.role import Role

__all__ = [
    "KeycloakPopulateService",
    "get_keycloak_populate_service",
    "keycloak_populate",
]


class InvalidUserCsvError(ValueError):
    """Die konfigurierte CSV-Datei enthält keine gültigen Keycloak-Benutzer."""


class KeycloakPopulateService:
    """Service für das Neuladen von Keycloak im Modus DEV."""

    def __init__(self, user_service: UserService) -> None:
        """Konstruktor mit abhängigem PatientRepository."""
        self.user_service: UserService = user_service

    def populate(self) -> None:
        """User-Daten in Keycloak über die REST-Schnittstelle neu laden."""
        if not dev_keycloak_populate:
            return

        logger.warning(">>> Keycloak wird neu geladen <<<")
        try:
            self._remove_users()
            self._create_users()
            logger.warning(">>> Keycloak wurde neu geladen <<<")
        except KeycloakConnectionError:
            logger.error(">>> Keine Keycloak-Verbindung! Ist Keycloak gestartet? <<<")

    def _remove_users(self) -> None:
        self.user_service.remove_all_users()
        logger.debug("Alle User außer 'admin' geloescht")

    def _create_users(self) -> None:
        logger.debug("Aktuelles Verzeichnis: {}", Path.cwd())
        csv_config_path = Path(csv_config)
        if not csv_config_path.is_file():
            logger.error(f"CSV-Datei {csv_config_path} existiert nicht")
            return
        logger.debug("CSV-Datei: {}", csv_config_path)

        with csv_config_path.open() as csv_file:
            csv_reader = DictReader(csv_file, delimiter=";")
            required_fields = {"email", "nachname", "username"}
            missing_fields = required_fields - set(csv_reader.fieldnames or [])
            if missing_fields:
                logger.error(
                    f"CSV-Datei {csv_config_path} fehlen Spalten: "
                    f"{', '.join(sorted(missing_fields))}"
                )
                raise InvalidUserCsvError

            for row_number, row in enumerate(csv_reader, start=2):
                username = row.get("username")
                if username == "admin":
                    continue

                email = row.get("email")
                nachname = row.get("nachname")
                if not username or not email or not nachname:
                    logger.error(
                        f"CSV-Datei {csv_config_path}, Zeile {row_number}: "
                        "username, email und nachname müssen ausgefüllt sein"
                    )
                    raise InvalidUserCsvError

                user = User(
                    username=username,
                    email=email,
                    nachname=nachname,
                    vorname=nachname,
                    roles=[Role.PATIENT],
                    password="p",  # ruff: ignore[hardcoded-password-func-arg] # NOSONAR
                )
                self.user_service.create_user(user=user)
        logger.debug("Alle User aus '{}' neu angelegt", csv_config_path)


def get_keycloak_populate_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> KeycloakPopulateService:
    """Factory-Funktion für TokenService."""
    return KeycloakPopulateService(user_service)


def keycloak_populate():
    """Keycloak mit Testdaten neu laden, falls im dev-Modus."""
    if dev_keycloak_populate:
        service = get_keycloak_populate_service(get_user_service())
        service.populate()
