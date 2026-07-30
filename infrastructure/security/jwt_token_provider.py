import jwt
import uuid
from datetime import datetime, timedelta, timezone
from application.ports.token_provider import TokenProvider
from application.dto.token_payload import TokenPayload
from application.exceptions.security_exceptions import (
    ExpiredTokenError, InvalidTokenError, SignatureVerificationError
)

class JwtTokenProvider(TokenProvider):
    def __init__(self, secret: str, expires_in_seconds: int = 3600, algorithm: str = "HS256"):
        self._secret = secret
        self._expires_in = expires_in_seconds
        self._algorithm = algorithm
        self._issuer = "cyberlab-auth"
        self._audience = "cyberlab-api"

    def create_token(self, user_id: str, role: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "iss": self._issuer,
            "aud": self._audience,
            "jti": uuid.uuid4().hex,
            "sub": user_id,
            "roles": [role], # Préparation multi-rôles
            "iat": now,
            "exp": now + timedelta(seconds=self._expires_in)
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm], audience=self._audience, issuer=self._issuer)
            return TokenPayload(
                user_id=payload["sub"],
                role=payload["roles"][0],
                issued_at=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
                expiration=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                claims=payload
            )
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError("Le jeton de session a expiré.")
        except jwt.InvalidSignatureError:
            raise SignatureVerificationError("Signature du jeton invalide.")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Jeton malformé ou non reconnu: {str(e)}")