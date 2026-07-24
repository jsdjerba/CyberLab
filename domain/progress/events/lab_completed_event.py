
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

@dataclass(frozen=True)
class LabCompletedEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str = field(default="")
    lab_id: str = field(default="")
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, student_id: str, lab_id: str, completed_at: datetime) -> "LabCompletedEvent":
        return cls(student_id=student_id, lab_id=lab_id, completed_at=completed_at)
