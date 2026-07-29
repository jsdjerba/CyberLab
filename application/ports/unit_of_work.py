from abc import ABC, abstractmethod
from typing import List, Any

class AbstractUnitOfWork(ABC):
    """
    Port (Interface) applicatif pour l'Unit of Work.
    Gère les limites transactionnelles et la coordination des repositories,
    tout en préparant la collecte des Domain Events.
    """
    
    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    @abstractmethod
    def commit(self) -> None:
        """Valide la transaction en cours et déclenche la persistance physique."""
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """Annule la transaction en cours en cas d'erreur."""
        raise NotImplementedError

    @abstractmethod
    def collect_events(self) -> List[Any]:
        """Collecte les Domain Events générés par les agrégats suivis."""
        raise NotImplementedError