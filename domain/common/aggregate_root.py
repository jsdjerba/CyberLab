from typing import List, Any

class AggregateRoot:
    """
    Classe de base pour tous les Aggregate Roots du domaine.
    Gère la collection volatile des Domain Events produits lors des mutations métier.
    """
    def __init__(self):
        self._events: List[Any] = []

    def register_event(self, event: Any) -> None:
        self._events.append(event)

    def collect_events(self) -> List[Any]:
        events = list(self._events)
        self._events.clear()
        return events

    def clear_events(self) -> None:
        self._events.clear()