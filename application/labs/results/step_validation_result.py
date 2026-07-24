from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class StepValidationResult:
    success: bool
    message: str
    score: int
    current_step: Optional[str]
    completed: bool