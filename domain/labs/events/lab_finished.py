from dataclasses import dataclass
from domain.labs.events.base import DomainEvent

@dataclass(frozen=True)
class LabFinished(DomainEvent):
    lab_instance_id: str
    final_score: int