from abc import ABC, abstractmethod
from typing import Any, Type
from application.ports.event_handler import AbstractEventHandler

class EventCascadeLimitExceeded(Exception):
    """
    Levée lorsque la profondeur de la cascade d'événements dépasse la limite autorisée.
    Prévient les boucles infinies (Stack Overflow) et la surcharge des threads HTTP.
    """
    pass

class AbstractEventBus(ABC):
    @abstractmethod
    def subscribe(self, event_type: Type[Any], handler: AbstractEventHandler) -> None:
        pass

    @abstractmethod
    def publish(self, event: Any) -> None:
        pass