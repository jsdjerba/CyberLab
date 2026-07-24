from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass(frozen=True)
class ProgressDTO:
    id: int
    student_id: int
    lab_id: int
    status: str
    completed_at: Optional[datetime]
    xp_earned: int