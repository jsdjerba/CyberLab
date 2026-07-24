from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class LabProgressResult:
    lab_id: str
    student_id: int
    status: str
    current_step: Optional[str]
    score: int
    completed_steps: List[str]