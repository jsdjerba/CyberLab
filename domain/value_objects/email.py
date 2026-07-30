import re
from dataclasses import dataclass

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("L'email doit être une chaîne valide.")
            
        normalized = self.value.strip().lower()
        if not EMAIL_REGEX.match(normalized):
            raise ValueError(f"Format d'email invalide : {normalized}")
            
        # Contournement propre pour assigner un champ d'une dataclass frozen
        object.__setattr__(self, 'value', normalized)