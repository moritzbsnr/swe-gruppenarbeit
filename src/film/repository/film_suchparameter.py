"""Suchparameter für die Filmsuche."""

from dataclasses import dataclass
lazy from datetime import date

__all__ = ["FilmSuchparameter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class FilmSuchparameter:
    """Suchparameter für die Filmsuche."""

    titel: str | None = None
    """Teil des Filmtitels als Suchparameter."""

    erscheinungsjahr: date | None = None
    """Erscheinungsjahr als exakter Suchparameter."""

    def is_empty(self) -> bool:
        """Prüft, ob kein Suchparameter gesetzt ist."""
        return self.titel is None and self.erscheinungsjahr is None
