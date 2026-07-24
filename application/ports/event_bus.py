from typing import Protocol, Any, Sequence

class EventBus(Protocol):
    def publish(self, events: Sequence[Any]) -> None:
        ...