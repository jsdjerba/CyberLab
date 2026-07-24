from dataclasses import dataclass
from domain.labs.value_objects.step_id import StepId

@dataclass(frozen=True)
class ProgressReport:
    """Value Object immuable représentant l'état de progression d'un laboratoire."""
    completion_percentage: float
    completed_steps: tuple[StepId, ...]
    remaining_steps: tuple[StepId, ...]
    next_available_steps: tuple[StepId, ...]
    is_finished: bool
    completed_count: int
    remaining_count: int

    @property
    def total_steps(self) -> int:
        return self.completed_count + self.remaining_count

    @property
    def has_remaining_steps(self) -> bool:
        return self.remaining_count > 0