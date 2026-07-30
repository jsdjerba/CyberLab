"""
Représente un mot de passe déjà haché.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class PasswordHash:
    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str) or not self.value.strip():
            raise ValueError("Le hash du mot de passe ne peut pas être vide.")
        
        # Le domaine pur ne vérifie pas la longueur bcrypt/argon2.
        # Il garantit simplement l'intégrité de l'état (non-vide).