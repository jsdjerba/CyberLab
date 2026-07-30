"""
Port applicatif pour la génération de jetons d'authentification (ex: JWT).
"""
from typing import Protocol

class TokenProvider(Protocol):
    def create_token(self, user_id: str, role: str) -> str:
        ...