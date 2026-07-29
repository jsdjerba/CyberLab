from dataclasses import dataclass
from domain.events.base_domain_event import BaseDomainEvent
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId

@dataclass(frozen=True, kw_only=True)
class FlagRejected(BaseDomainEvent):
    """Émis lorsqu'une tentative est fausse ou bloquée (ex: Rate Limiting)."""
    student_id: StudentId
    lab_id: LabId
    objective_id: ObjectiveId
    reason: str