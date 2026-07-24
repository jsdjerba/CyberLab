from abc import ABC, abstractmethod
from domain.labs.entities.step import Step

class FlagValidator(ABC):
    @abstractmethod
    def validate(self, step: Step, submitted_flag: str) -> bool:
        """Valide si le flag soumis correspond à l'étape donnée."""
        pass