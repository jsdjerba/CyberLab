from dataclasses import dataclass
from typing import List
from domain.labs.value_objects.step_id import StepId

@dataclass(frozen=True)
class ProgressReport:
    """Représente l'état d'avancement calculé d'un apprenant."""
    completion_percentage: float
    completed_steps: List[StepId]
    remaining_steps: List[StepId]
    next_available_steps: List[StepId]
    is_finished: bool