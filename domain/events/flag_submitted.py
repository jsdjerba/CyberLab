"""
Événement de domaine : FlagSubmitted.
"""

from dataclasses import dataclass
from domain.events.base_domain_event import BaseDomainEvent
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.attempt_id import AttemptId


@dataclass(frozen=True, kw_only=True)
class FlagSubmitted(BaseDomainEvent):
    student_id: StudentId | str
    lab_id: LabId | str
    objective_id: ObjectiveId | str = "obj-default"  # Valeur par défaut pour les vieux tests d'événements
    attempt_id: AttemptId | str | None = None
    attempt_number: int | None = None

    def __post_init__(self):
        if self.attempt_id is None and self.attempt_number is not None:
            object.__setattr__(self, 'attempt_id', AttemptId(f"att-{self.attempt_number}"))