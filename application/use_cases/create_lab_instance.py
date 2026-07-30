"""
Use Case : Création d'une instance de laboratoire à l'état initial (NOT_STARTED).
"""

from dataclasses import dataclass
from typing import Optional, Any
from domain.entities.lab_instance import LabInstance
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from application.ports.lab_instance_repository import LabInstanceRepository
from application.ports.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class CreateLabInstanceCommand:
    student_id: str
    lab_id: str
    objectives: Optional[list[Any]] = None


@dataclass(frozen=True)
class CreateLabInstanceResult:
    student_id: str
    lab_id: str
    status: str


class CreateLabInstanceUseCase:
    """Orchestre la création et la persistance d'une nouvelle instance de laboratoire."""

    def __init__(self, repository: LabInstanceRepository, uow: UnitOfWork):
        self._repository = repository
        self._uow = uow

    def execute(self, command: CreateLabInstanceCommand) -> CreateLabInstanceResult:
        s_id = StudentId(command.student_id)
        l_id = LabId(command.lab_id)

        # Vérification d'unicité ou idempotence de création
        existing = self._repository.find_by_id(s_id.value, l_id.value)
        if existing:
            return CreateLabInstanceResult(
                student_id=existing.student_id.value,
                lab_id=existing.lab_id.value,
                status=existing.status.name
            )

        instance = LabInstance(
            student_id=s_id,
            lab_id=l_id,
            objectives=command.objectives
        )

        with self._uow:
            self._repository.save(instance)
            self._uow.commit()

        return CreateLabInstanceResult(
            student_id=instance.student_id.value,
            lab_id=instance.lab_id.value,
            status=instance.status.name
        )