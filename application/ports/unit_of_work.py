"""
Port Unit of Work (Clean Architecture).
Définit les contrats d'abstraction pour la gestion transactionnelle.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class UnitOfWork(Protocol):
    """Contrat d'abstraction agnostique pour l'Unit of Work."""

    def __enter__(self) -> "UnitOfWork":
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


# Alias de rétrocompatibilité pour les tests existants du projet
AbstractUnitOfWork = UnitOfWork