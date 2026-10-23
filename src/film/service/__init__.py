"""Modul für den Geschäftslogik."""

from film.service.adresse_dto import AdresseDTO
from film.service.exceptions import (
    EmailExistsError,
    ForbiddenError,
    NotFoundError,
    UsernameExistsError,
    VersionOutdatedError,
)
from film.service.mailer import send_mail
from film.service.patient_dto import PatientDTO
from film.service.patient_service import PatientService
from film.service.patient_write_service import PatientWriteService

# https://docs.python.org/3/tutorial/modules.html#importing-from-a-package
__all__ = [
    "AdresseDTO",
    "EmailExistsError",
    "ForbiddenError",
    "NotFoundError",
    "PatientDTO",
    "PatientService",
    "PatientWriteService",
    "UsernameExistsError",
    "VersionOutdatedError",
    "send_mail",
]
