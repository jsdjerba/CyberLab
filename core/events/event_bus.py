import logging
import time
import threading
from typing import Type
from domain.events.event import DomainEvent
from core.events.event_handler import IEventHandler
from core.events.exceptions import EventProcessingError, HandlerNotFound

class EventBus:
    def __init__(self, strict: bool = False, logger: logging.Logger | None = None):
        self._handlers: dict[Type[DomainEvent], list[IEventHandler]] = {}
        self.strict = strict
        self._logger = logger or logging.getLogger(__name__)
        self._lock = threading.RLock()

    def get_handler_count(self, event_type: Type[DomainEvent]) -> int:
        """API publique minimale pour inspecter l'état (utilisée par les tests)."""
        with self._lock:
            return len(self._handlers.get(event_type, []))

    def has_handler(self, event_type: Type[DomainEvent], handler: IEventHandler) -> bool:
        """API publique pour vérifier l'enregistrement d'un handler spécifique."""
        with self._lock:
            return handler in self._handlers.get(event_type, [])

    def register(self, event_type: Type[DomainEvent], handler: IEventHandler) -> None:
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            
            # Idempotence: on évite les doublons
            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)
                self._logger.debug(
                    "Registered handler %s for event %s",
                    handler.__class__.__name__,
                    event_type.__name__
                )
            else:
                self._logger.debug(
                    "Handler %s is already registered for event %s. Skipping.",
                    handler.__class__.__name__,
                    event_type.__name__
                )

    def unregister(self, event_type: Type[DomainEvent], handler: IEventHandler) -> None:
        with self._lock:
            if event_type in self._handlers and handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                self._logger.debug(
                    "Unregistered handler %s for event %s",
                    handler.__class__.__name__,
                    event_type.__name__
                )

    def clear_handlers(self) -> None:
        with self._lock:
            self._handlers.clear()
            self._logger.debug("Cleared all event handlers from EventBus")

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        
        # Copie de la liste des handlers sous verrou pour éviter 
        # les erreurs d'itération si la liste est modifiée dynamiquement
        with self._lock:
            handlers = list(self._handlers.get(event_type, []))

        if not handlers:
            if self.strict:
                raise HandlerNotFound(f"No handlers registered for event {event_type.__name__}")
            self._logger.debug("No handlers found for event %s. Ignoring.", event_type.__name__)
            return

        self._logger.info("Publishing %s to %d handler(s)", event_type.__name__, len(handlers))

        for handler in handlers:
            handler_name = handler.__class__.__name__
            start_time = time.perf_counter()
            try:
                handler.handle(event)
                duration = (time.perf_counter() - start_time) * 1000
                self._logger.info(
                    "Handler %s processed %s in %.2fms",
                    handler_name,
                    event_type.__name__,
                    duration
                )
            except Exception as e:
                duration = (time.perf_counter() - start_time) * 1000
                # Log l'exception technique complète pour les développeurs
                self._logger.error(
                    "Handler %s failed processing %s after %.2fms",
                    handler_name,
                    event_type.__name__,
                    duration,
                    exc_info=True
                )
                # Lève une erreur encapsulée métier propre
                raise EventProcessingError(
                    event_type=event_type.__name__,
                    handler_name=handler_name,
                    cause=e
                ) from e

    def publish_many(self, events: list[DomainEvent]) -> None:
        for event in events:
            self.publish(event)