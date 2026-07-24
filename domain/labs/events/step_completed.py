from dataclasses import dataclass
from domain.labs.events.base import DomainEvent

@dataclass(frozen=True)
class StepCompleted(DomainEvent):
    lab_instance_id: str
    step_id: str
    score_awarded: int