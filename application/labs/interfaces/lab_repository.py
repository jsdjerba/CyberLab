from abc import ABC, abstractmethod
from typing import Optional
from domain.labs.entities.lab import Lab
from domain.labs.value_objects.lab_id import LabId

class LabRepository(ABC):
    @abstractmethod
    def get_by_id(self, lab_id: LabId) -> Optional[Lab]:
        """Récupère la définition d'un laboratoire par son ID."""
        pass