from dataclasses import dataclass
from datetime import timedelta
from domain.events.base_domain_event import BaseDomainEvent
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId

@dataclass(frozen=True, kw_only=True)
class LabLockedOut(BaseDomainEvent):
    """Émis lorsque la politique anti-bruteforce (AttemptPolicy) verrouille le lab."""
    student_id: StudentId
    lab_id: LabId
    lockout_duration: timedelta

    def __post_init__(self):
        # Exécution du __post_init__ parent si existant (ex: pour générer le timestamp)
        try:
            super().__post_init__()
        except AttributeError:
            pass
            
        if self.lockout_duration.total_seconds() < 0:
            raise ValueError("La durée de blocage ne peut pas être négative")