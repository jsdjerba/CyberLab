
from typing import Protocol, Sequence, Any

class EventPublisher(Protocol):
    def publish(self, events: Sequence[Any]) -> None:
        ...
