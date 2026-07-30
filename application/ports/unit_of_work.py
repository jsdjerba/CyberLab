"""Port abstrait unifié pour la gestion des transactions (Unit of Work)."""
from typing import Protocol, Sequence, Any, runtime_checkable

@runtime_checkable
class UnitOfWork(Protocol):
    def begin(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def register_events(self, events: Sequence[Any]) -> None:
        ...

    def collect_events(self) -> Sequence[Any]:
        ...

    def __enter__(self) -> 'UnitOfWork':
        ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        ...


# --- Rétrocompatibilité pour l'Infrastructure Existante ---
# Permet d'éviter le crash d'import sur SqlAlchemyUnitOfWork qui hérite de AbstractUnitOfWork
class AbstractUnitOfWork(UnitOfWork):
    """Classe de compatibilité pour les adaptateurs d'infrastructure existants."""
    def __enter__(self) -> 'AbstractUnitOfWork':
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()