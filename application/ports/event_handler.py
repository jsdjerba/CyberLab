from abc import ABC, abstractmethod
from typing import Any

class AbstractEventHandler(ABC):
    """Contrat pour tous les gestionnaires (subscribers) de Domain Events."""

    @abstractmethod
    def handle(self, event: Any) -> None:
        """Traite un événement métier du domaine."""
        raise NotImplementedError