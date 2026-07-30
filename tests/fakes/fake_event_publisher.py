
from typing import Sequence, Any
from application.ports.event_publisher import EventPublisher

class FakeEventPublisher(EventPublisher):
    def __init__(self):
        self.published_events = []

    def publish(self, events: Sequence[Any]) -> None:
        self.published_events.extend(events)
