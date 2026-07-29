import re
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class FlagHash:
    value: str

    def __post_init__(self):
        if not self.value or not str(self.value).strip():
            raise ValueError("Le hash ne peut pas être vide.")
            
        # Protection métier : un hash ne doit jamais contenir la structure d'un flag en clair
        if re.search(r"CTF\{.*?\}", str(self.value), re.IGNORECASE):
            raise ValueError("Le hash ne peut pas contenir un flag en clair.")