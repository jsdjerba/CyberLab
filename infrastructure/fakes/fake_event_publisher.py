from typing import List, Dict, Type
from application.common.interfaces.event_publisher import EventPublisher, EventHandler
from domain.labs.events.base import DomainEvent

class FakeEventPublisher(EventPublisher):
    def __init__(self):
        self.published_events: List[DomainEvent] = []
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)
        
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler.handle(event)

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)