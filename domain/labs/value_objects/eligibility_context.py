from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class EligibilityContext:
    student_level: str
    active_classroom_id: str
    completed_lab_ids: Tuple[str, ...]