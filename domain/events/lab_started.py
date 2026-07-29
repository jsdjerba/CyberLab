from dataclasses import dataclass
from domain.events.base_domain_event import BaseDomainEvent
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId

@dataclass(frozen=True, kw_only=True)
class LabStarted(BaseDomainEvent):
    """Émis lorsqu'un étudiant démarre officiellement un laboratoire."""
    student_id: StudentId
    lab_id: LabId