from typing import Protocol
from domain.events.event import DomainEvent

class IEventHandler(Protocol):
    """Interface stricte pour tous les consommateurs d'événements."""
    def handle(self, event: DomainEvent) -> None:
        ...