"""
Use Case : Soumission et évaluation d'un drapeau (Flag).
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.correlation_id import CorrelationId
from domain.value_objects.attempt_id import AttemptId
from domain.exceptions import LabInstanceNotFoundError
from application.ports.lab_instance_repository import LabInstanceRepository
from application.ports.flag_validator import FlagValidator
from application.ports.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class SubmitFlagCommand:
    student_id: str
    lab_id: str
    objective_id: str
    submitted_flag: str
    correlation_id: str
    attempt_id: Optional[str] = None
    current_time: Optional[datetime] = None  # Ajouté pour la rétrocompatibilité des tests


@dataclass(frozen=True)
class SubmitFlagResult:
    student_id: str
    lab_id: str
    objective_id: str
    is_correct: bool
    status: str
    correlation_id: str


class SubmitFlagUseCase:
    """Orchestre l'évaluation de la soumission d'un flag et la mise à jour de l'agrégat."""

    def __init__(self, repository: LabInstanceRepository, validator: FlagValidator, uow: Optional[UnitOfWork] = None):
        self._repository = repository
        self._validator = validator
        self._uow = uow

    def execute(self, command: SubmitFlagCommand) -> SubmitFlagResult:
        s_id = StudentId(command.student_id)
        l_id = LabId(command.lab_id)
        obj_id = ObjectiveId(command.objective_id)
        corr_id = CorrelationId(command.correlation_id)
        att_id = AttemptId(command.attempt_id) if command.attempt_id else None

        instance = self._repository.find_by_id(s_id.value, l_id.value)
        if not instance:
            raise LabInstanceNotFoundError(f"Instance introuvable pour {s_id} / {l_id}")

        is_correct = instance.submit_flag(
            objective_id=obj_id,
            submitted_flag=command.submitted_flag,
            validator=self._validator,
            correlation_id=corr_id,
            attempt_id=att_id,
            current_time=command.current_time  # Transmis à l'agrégat
        )

        if self._uow:
            with self._uow:
                self._repository.save(instance)
                self._uow.commit()
        else:
            self._repository.save(instance)

        return SubmitFlagResult(
            student_id=instance.student_id.value,
            lab_id=instance.lab_id.value,
            objective_id=obj_id.value,
            is_correct=is_correct,
            status=instance.status.name,
            correlation_id=corr_id.value
        )