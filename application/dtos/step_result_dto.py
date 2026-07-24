from dataclasses import dataclass

@dataclass(frozen=True)
class StepResultDto:
    step_id: str
    is_valid: bool
    points_awarded: int
    message: str