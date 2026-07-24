from dataclasses import dataclass
from domain.labs.value_objects.student_id import StudentId

@dataclass(frozen=True)
class LifecycleContext:
    """Contexte d'exécution lors du changement d'état d'un laboratoire."""
    student_id: StudentId
    triggered_by_admin: bool = False
    reason: str = ""