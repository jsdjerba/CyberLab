"""
Port Flag Validator (Clean Architecture).
Définit le contrat d'évaluation des drapeaux de cybersécurité.
"""

from typing import Protocol
from domain.value_objects.objective_id import ObjectiveId


class FlagValidator(Protocol):
    """Contrat d'évaluation des soumissions de flags."""

    def validate(self, submitted_flag: str, objective_id: ObjectiveId) -> bool:
        ...