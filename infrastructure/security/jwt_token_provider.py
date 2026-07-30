"""
Adaptateur d'infrastructure pour la génération de jetons JWT.
"""
import jwt
from datetime import datetime, timedelta, timezone
from application.ports.token_provider import TokenProvider

class JwtTokenProvider(TokenProvider):
    def __init__(self, secret: str, expires_in_seconds: int = 3600, algorithm: str = "HS256"):
        self._secret = secret
        self._expires_in = expires_in_seconds
        self._algorithm = algorithm

    def create_token(self, user_id: str, role: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "role": role,
            "iat": now,
            "exp": now + timedelta(seconds=self._expires_in)
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)