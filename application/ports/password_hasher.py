"""
Port applicatif pour le hashage de mot de passe.
"""
from typing import Protocol
from domain.value_objects.password_hash import PasswordHash

class PasswordHasher(Protocol):
    def hash(self, plaintext_password: str) -> PasswordHash:
        ...

    def verify(self, plaintext_password: str, hashed_password: PasswordHash) -> bool:
        ...