from abc import ABC, abstractmethod
from application.labs.interfaces.lab_repository import LabRepository
from application.labs.interfaces.lab_instance_repository import LabInstanceRepository

class UnitOfWork(ABC):
    labs: LabRepository
    lab_instances: LabInstanceRepository

    def __enter__(self) -> 'UnitOfWork':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()

    @abstractmethod
    def commit(self) -> None:
        """Valide la transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Annule la transaction."""
        pass