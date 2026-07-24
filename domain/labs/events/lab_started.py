from dataclasses import dataclass
from domain.labs.events.base import DomainEvent

@dataclass(frozen=True)
class LabStarted(DomainEvent):
    lab_instance_id: str