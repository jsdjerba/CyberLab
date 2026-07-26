from typing import Sequence, Any

class EventBusAdapter:
    """
    Adaptateur minimal pour l'EventBus.
    Conforme au protocole EventBus de la couche Application.
    """
    def __init__(self):
        self.dispatched_events: list = []

    def publish(self, events: Sequence[Any]) -> None:
        """
        Reçoit une séquence d'événements et les enregistre/dispatche.
        """
        for event in events:
            self.dispatched_events.append(event)