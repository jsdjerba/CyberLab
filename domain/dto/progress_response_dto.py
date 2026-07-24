
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.progress.entities.progress import Progress
from domain.progress.value_objects.progress_status import ProgressStatus


@dataclass(frozen=True)
class ProgressResponseDTO:
    """Immutable output boundary object. Decouples API serialization from domain entity."""
    progress_id: str
    student_id: str
    lab_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]

    @classmethod
    def from_entity(cls, progress: Progress) -> "ProgressResponseDTO":
        return cls(
            progress_id=progress.progress_id,
            student_id=progress.student_id,
            lab_id=progress.lab_id,
            status=progress.status.value,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
        )
