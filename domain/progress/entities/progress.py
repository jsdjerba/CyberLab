
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List
import uuid

from domain.progress.value_objects.progress_status import ProgressStatus
from domain.progress.events.lab_completed_event import LabCompletedEvent
from domain.exceptions import InvalidProgressTransitionError, LabAlreadyCompletedError


@dataclass
class Progress:
    """
    Progress Entity - Aggregate Root.
    Encapsulates the lifecycle of a student's lab progression.
    Pure domain object: no Flask, no SQLAlchemy, no infrastructure knowledge.
    """
    student_id: str
    lab_id: str
    progress_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ProgressStatus = field(default=ProgressStatus.STARTED)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = field(default=None)

    _pending_events: List[LabCompletedEvent] = field(default_factory=list, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.student_id:
            raise ValueError("student_id is required and immutable")
        if not self.lab_id:
            raise ValueError("lab_id is required and immutable")

    @classmethod
    def start(cls, student_id: str, lab_id: str) -> "Progress":
        return cls(student_id=student_id, lab_id=lab_id)

    def complete(self, now: Optional[datetime] = None) -> None:
        """
        Transitions progression from STARTED to COMPLETED.
        Raises domain exceptions if the invariant is violated.
        Collects a LabCompletedEvent for later publication by the Application layer.
        """
        if self.status == ProgressStatus.COMPLETED:
            raise LabAlreadyCompletedError(
                f"Lab '{self.lab_id}' already completed for student '{self.student_id}'"
            )
        if not self.status.can_transition_to(ProgressStatus.COMPLETED):
            raise InvalidProgressTransitionError(
                f"Cannot transition from {self.status} to COMPLETED"
            )

        completion_time = now or datetime.now(timezone.utc)
        self.status = ProgressStatus.COMPLETED
        self.completed_at = completion_time

        event = LabCompletedEvent.create(
            student_id=self.student_id,
            lab_id=self.lab_id,
            completed_at=completion_time,
        )
        self._pending_events.append(event)

    def is_completed(self) -> bool:
        return self.status == ProgressStatus.COMPLETED

    def belongs_to(self, student_id: str) -> bool:
        return self.student_id == student_id

    def pull_events(self) -> List[LabCompletedEvent]:
        """Returns and clears pending domain events. Entity never publishes events itself."""
        events = list(self._pending_events)
        self._pending_events.clear()
        return events
