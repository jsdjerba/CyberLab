from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError
)

class PasswordHasher:
    _hasher = Argon2Hasher()

    @staticmethod
    def hash_password(password: str) -> str:
        return PasswordHasher._hasher.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            return PasswordHasher._hasher.verify(hashed_password, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False