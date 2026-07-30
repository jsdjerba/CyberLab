"""
Schémas de validation et DTOs pour la couche de présentation (Presentation DTOs).
Assurent la validation stricte des charges utiles HTTP entrantes.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateLabInstanceRequestDTO:
    student_id: str

    @staticmethod
    def from_dict(data: dict) -> "CreateLabInstanceRequestDTO":
        if not data or not isinstance(data, dict):
            raise ValueError("Payload JSON invalide.")
        student_id = data.get("student_id")
        if not student_id or not isinstance(student_id, str):
            raise ValueError("Le champ 'student_id' est obligatoire et doit être une chaîne de caractères.")
        return CreateLabInstanceRequestDTO(student_id=student_id.strip())


@dataclass(frozen=True)
class StartLabRequestDTO:
    correlation_id: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "StartLabRequestDTO":
        if not data:
            return StartLabRequestDTO(correlation_id=None)
        corr_id = data.get("correlation_id")
        return StartLabRequestDTO(correlation_id=str(corr_id) if corr_id else None)