from dataclasses import dataclass
from domain.events.base_domain_event import BaseDomainEvent
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.completion_time import CompletionTime

@dataclass(frozen=True, kw_only=True)
class LabCompleted(BaseDomainEvent):
    """Émis lorsque la CompletionPolicy du laboratoire est pleinement satisfaite."""
    student_id: StudentId
    lab_id: LabId
    completion_time: CompletionTime