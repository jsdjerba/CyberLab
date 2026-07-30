"""
Use Case : Récupération en lecture seule de l'état d'une instance de laboratoire.
"""

from dataclasses import dataclass
from typing import Any, List
from domain.exceptions import LabInstanceNotFoundError
from application.ports.lab_instance_repository import LabInstanceRepository


@dataclass(frozen=True)
class GetLabInstanceQuery:
    student_id: str
    lab_id: str


@dataclass(frozen=True)
class LabInstanceDetailsDTO:
    student_id: str
    lab_id: str
    status: str
    objectives: List[dict]
    attempts_count: int


class GetLabInstanceUseCase:
    """Orchestre la récupération sécurisée d'une instance de lab pour affichage."""

    def __init__(self, repository: LabInstanceRepository):
        self._repository = repository

    def execute(self, query: GetLabInstanceQuery) -> LabInstanceDetailsDTO:
        instance = self._repository.find_by_id(query.student_id, query.lab_id)
        if not instance:
            raise LabInstanceNotFoundError(f"Instance introuvable pour {query.student_id} / {query.lab_id}")

        objectives_data = [
            {
                "objective_id": obj.objective_id.value,
                "score_weight": obj.score_weight,
                "is_completed": obj.is_completed
            }
            for obj in instance.objectives
        ]

        return LabInstanceDetailsDTO(
            student_id=instance.student_id.value,
            lab_id=instance.lab_id.value,
            status=instance.status.name,
            objectives=objectives_data,
            attempts_count=len(instance.attempts)
        )