"""
Adaptateur d'infrastructure pour le hachage sécurisé (Bcrypt).
"""
import bcrypt
from application.ports.password_hasher import PasswordHasher
from domain.value_objects.password_hash import PasswordHash

class BcryptPasswordHasher(PasswordHasher):
    def hash(self, plaintext_password: str) -> PasswordHash:
        # Hachage fort (salt automatique intégré)
        hashed_bytes = bcrypt.hashpw(plaintext_password.encode('utf-8'), bcrypt.gensalt())
        return PasswordHash(hashed_bytes.decode('utf-8'))

    def verify(self, plaintext_password: str, hashed_password: PasswordHash) -> bool:
        return bcrypt.checkpw(
            plaintext_password.encode('utf-8'),
            hashed_password.value.encode('utf-8')
        )