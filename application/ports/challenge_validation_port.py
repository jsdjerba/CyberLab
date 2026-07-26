from typing import Protocol
from application.dtos.validation_result_dto import ValidationResult

class ChallengeValidationPort(Protocol):
    def validate(self, lab_id: str, step_id: str, submitted_answer: str) -> ValidationResult:
        """
        Valide une réponse soumise pour une étape d'un laboratoire.
        L'implémentation masquera la récupération du secret et l'appel au service métier.
        """
        ...