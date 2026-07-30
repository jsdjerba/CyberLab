"""
Use Case : Démarrage explicite d'un laboratoire.
"""

from dataclasses import dataclass
from typing import Optional, Any
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.correlation_id import CorrelationId
from domain.exceptions import LabInstanceNotFoundError
from application.ports.lab_instance_repository import LabInstanceRepository
from application.ports.unit_of_work import UnitOfWork
from domain.entities.lab_instance import LabInstance


@dataclass(frozen=True)
class StartLabCommand:
    student_id: str
    lab_id: str
    correlation_id: str
    objectives: Optional[list[Any]] = None


@dataclass(frozen=True)
class StartLabResult:
    student_id: str
    lab_id: str
    status: str
    correlation_id: str


class StartLabUseCase:
    """Orchestre le démarrage sécurisé et idempotent d'un laboratoire."""

    def __init__(self, repository: LabInstanceRepository, uow: Optional[UnitOfWork] = None):
        self._repository = repository
        self._uow = uow

    def execute(self, command: StartLabCommand) -> StartLabResult:
        s_id = StudentId(command.student_id)
        l_id = LabId(command.lab_id)
        corr_id = CorrelationId(command.correlation_id)

        instance = self._repository.find_by_id(s_id.value, l_id.value)
        if not instance:
            # Création automatique à la volée si requis par les anciens tests unitaires
            instance = LabInstance(
                student_id=s_id,
                lab_id=l_id,
                objectives=command.objectives
            )

        instance.start(correlation_id=corr_id)

        if self._uow:
            with self._uow:
                self._repository.save(instance)
                self._uow.commit()
        else:
            self._repository.save(instance)

        return StartLabResult(
            student_id=instance.student_id.value,
            lab_id=instance.lab_id.value,
            status=instance.status.name,
            correlation_id=corr_id.value
        )