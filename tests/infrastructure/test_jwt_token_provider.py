import jwt
from infrastructure.security.jwt_token_provider import JwtTokenProvider

# RFC 7518 exige une clé d'au moins 32 octets (caractères) pour l'algorithme HS256
SECURE_TEST_SECRET = "cyberlab_test_secret_key_minimum_32_bytes_long"

def test_jwt_token_creation_and_payload():
    provider = JwtTokenProvider(secret=SECURE_TEST_SECRET, expires_in_seconds=3600)
    token = provider.create_token(user_id="u-123", role="ADMIN")
    
    decoded = jwt.decode(token, SECURE_TEST_SECRET, algorithms=["HS256"])
    assert decoded["sub"] == "u-123"
    assert decoded["role"] == "ADMIN"
    assert "exp" in decoded