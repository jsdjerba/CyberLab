import logging
from typing import Type, Dict, List, Any
from application.ports.event_bus import AbstractEventBus, EventCascadeLimitExceeded
from application.ports.event_handler import AbstractEventHandler

logger = logging.getLogger(__name__)

class InMemoryEventBus(AbstractEventBus):
    MAX_EVENT_DEPTH = 1

    def __init__(self):
        self._subscribers: Dict[Type[Any], List[AbstractEventHandler]] = {}
        self._current_depth = 0

    def subscribe(self, event_type: Type[Any], handler: AbstractEventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def publish(self, event: Any) -> None:
        if self._current_depth > self.MAX_EVENT_DEPTH:
            raise EventCascadeLimitExceeded(
                "Profondeur maximale de cascade d'événements dépassée."
            )

        self._current_depth += 1
        
        try:
            event_type = type(event)
            handlers = self._subscribers.get(event_type, [])
            correlation_id = getattr(event, 'correlation_id', 'unknown')
            
            for handler in handlers:
                handler_name = handler.__class__.__name__
                try:
                    handler.handle(event)
                    
                    logger.info(
                        f"Event dispatched: type={event_type.__name__} "
                        f"correlation_id={correlation_id} handler={handler_name}"
                    )
                except EventCascadeLimitExceeded:
                    # Ne jamais masquer l'exception de sécurité de la cascade
                    raise
                except Exception as e:
                    # Isolation des autres erreurs métier/techniques des handlers
                    logger.error(
                        f"Erreur inattendue dans le handler {handler_name} "
                        f"lors du traitement de l'événement {event_type.__name__} "
                        f"(correlation_id={correlation_id}): {e}",
                        exc_info=True
                    )
        finally:
            self._current_depth -= 1