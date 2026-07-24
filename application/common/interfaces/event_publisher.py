from abc import ABC, abstractmethod
from domain.labs.events.base import DomainEvent

class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        """Traite un événement métier spécifique."""
        pass

class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publie un événement vers les handlers souscrits."""
        pass

    @abstractmethod
    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """Souscrit un handler à un type d'événement précis."""
        pass