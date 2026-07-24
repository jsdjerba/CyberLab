import hashlib
import secrets

class FlagValidator:
    @staticmethod
    def verify(expected_hash: str, submitted_flag: str) -> bool:
        submitted_hash = hashlib.sha256(
            submitted_flag.encode("utf-8")
        ).hexdigest()
        return secrets.compare_digest(expected_hash, submitted_hash)