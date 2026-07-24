from typing import Protocol

class PasswordHasher(Protocol):
    """Abstraction pour la gestion des mots de passe.
    L'implémentation réelle (ex: BcryptHasher) sera injectée par l'infrastructure."""
    
    def hash(self, password: str) -> str:
        ...
        
    def verify(self, password: str, hashed_password: str) -> bool:
        ...