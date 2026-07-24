
from enum import Enum

class ProgressStatus(str, Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"

    def can_transition_to(self, target: "ProgressStatus") -> bool:
        allowed = {
            ProgressStatus.STARTED: {ProgressStatus.COMPLETED},
            ProgressStatus.COMPLETED: set(),
        }
        return target in allowed[self]
