from dataclasses import dataclass
from domain.events.base_domain_event import BaseDomainEvent
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId

@dataclass(frozen=True, kw_only=True)
class ObjectiveCompleted(BaseDomainEvent):
    """Émis lorsqu'un objectif métier spécifique d'un lab est déclaré accompli."""
    student_id: StudentId
    lab_id: LabId
    objective_id: ObjectiveId