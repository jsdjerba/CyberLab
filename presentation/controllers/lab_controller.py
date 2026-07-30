"""
Contrôleur de présentation pour les instances de laboratoire.
Ne contient aucune logique métier et délègue strictement aux Use Cases.
"""

from typing import Any
from presentation.schemas.lab_schema import CreateLabInstanceRequestDTO, StartLabRequestDTO
from presentation.schemas.flag_schema import SubmitFlagRequestDTO
from application.use_cases.create_lab_instance import CreateLabInstanceCommand
from application.use_cases.start_lab import StartLabCommand
from application.use_cases.submit_flag import SubmitFlagCommand
from application.use_cases.get_lab_instance import GetLabInstanceQuery
from domain.entities.objective import Objective
from domain.value_objects.objective_id import ObjectiveId


class LabController:
    """Contrôleur gérant la médiation entre l'API Flask et la couche Application."""

    def __init__(self, container: Any):
        self._container = container

    def create_instance(self, lab_id: str, raw_data: dict) -> dict:
        dto = CreateLabInstanceRequestDTO.from_dict(raw_data)
        use_case = self._container.create_lab_instance_use_case()
        
        # Injection d'un objectif par défaut pour le mode Offline/CTF si non fourni
        default_objective = Objective(
            objective_id=ObjectiveId("obj-1"),
            score_weight=10,
            is_completed=False
        )

        command = CreateLabInstanceCommand(
            student_id=dto.student_id,
            lab_id=lab_id,
            objectives=[default_objective]
        )
        result = use_case.execute(command)
        
        return {
            "student_id": result.student_id,
            "lab_id": result.lab_id,
            "status": result.status
        }

    def start_instance(self, lab_id: str, student_id: str, raw_data: dict, correlation_id: str) -> dict:
        dto = StartLabRequestDTO.from_dict(raw_data)
        corr_id = dto.correlation_id if dto.correlation_id else correlation_id
        
        use_case = self._container.start_lab_use_case()
        command = StartLabCommand(
            student_id=student_id,
            lab_id=lab_id,
            correlation_id=corr_id
        )
        result = use_case.execute(command)

        return {
            "student_id": result.student_id,
            "lab_id": result.lab_id,
            "status": result.status,
            "correlation_id": result.correlation_id
        }

    def submit_flag(self, lab_id: str, student_id: str, raw_data: dict, correlation_id: str) -> dict:
        dto = SubmitFlagRequestDTO.from_dict(raw_data)
        corr_id = dto.correlation_id if dto.correlation_id else correlation_id

        use_case = self._container.submit_flag_use_case()
        command = SubmitFlagCommand(
            student_id=student_id,
            lab_id=lab_id,
            objective_id=dto.objective_id,
            submitted_flag=dto.flag,
            correlation_id=corr_id
        )
        result = use_case.execute(command)

        return {
            "success": True,
            "validated": result.is_correct,
            "status": result.status,
            "request_id": correlation_id
        }

    def get_instance_status(self, lab_id: str, student_id: str) -> dict:
        use_case = self._container.get_lab_instance_use_case()
        query = GetLabInstanceQuery(student_id=student_id, lab_id=lab_id)
        result = use_case.execute(query)

        return {
            "student_id": result.student_id,
            "lab_id": result.lab_id,
            "status": result.status,
            "objectives": result.objectives,
            "attempts_count": result.attempts_count
        }