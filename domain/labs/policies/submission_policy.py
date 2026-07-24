from dataclasses import dataclass
from typing import Optional
from domain.labs.exceptions import InvalidSubmissionPolicy

@dataclass(frozen=True)
class SubmissionPolicy:
    """Politique de soumission basée sur un quota optionnel et un délai de cooldown.
    
    - max_attempts = None : tentatives illimitées
    - max_attempts = 0 : aucune tentative autorisée
    - max_attempts > 0 : nombre maximal d'essais
    """
    max_attempts: Optional[int]
    cooldown_seconds: int

    def __post_init__(self) -> None:
        if self.cooldown_seconds < 0:
            raise InvalidSubmissionPolicy("Le cooldown ne peut pas être négatif.")
        if self.max_attempts is not None and self.max_attempts < 0:
            raise InvalidSubmissionPolicy("Le nombre maximal d'essais ne peut pas être négatif.")