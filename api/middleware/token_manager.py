import base64
import hmac
import hashlib
import json
import time
from domain.exceptions import InvalidCredentials

class TokenManager:
    def __init__(self, secret_key: str):
        self.secret = secret_key.encode('utf-8')

    def _b64_encode(self, data: dict) -> str:
        json_str = json.dumps(data, separators=(',', ':')).encode('utf-8')
        return base64.urlsafe_b64encode(json_str).decode('utf-8').rstrip('=')

    def _b64_decode(self, data: str) -> dict:
        padding = '=' * (-len(data) % 4)
        json_str = base64.urlsafe_b64decode(data + padding).decode('utf-8')
        return json.loads(json_str)

    def generate_token(self, payload: dict, expires_in: int = 3600) -> str:
        header = self._b64_encode({"alg": "HS256", "typ": "JWT"})
        
        payload_copy = payload.copy()
        payload_copy['exp'] = int(time.time()) + expires_in
        enc_payload = self._b64_encode(payload_copy)

        signature = hmac.new(self.secret, f"{header}.{enc_payload}".encode('utf-8'), hashlib.sha256).digest()
        enc_signature = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')

        return f"{header}.{enc_payload}.{enc_signature}"

    def verify_token(self, token: str) -> dict:
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise InvalidCredentials("Invalid token format.")

            header, enc_payload, enc_signature = parts

            expected_sig = hmac.new(self.secret, f"{header}.{enc_payload}".encode('utf-8'), hashlib.sha256).digest()
            expected_enc_sig = base64.urlsafe_b64encode(expected_sig).decode('utf-8').rstrip('=')

            if not hmac.compare_digest(enc_signature, expected_enc_sig):
                raise InvalidCredentials("Invalid token signature.")

            payload = self._b64_decode(enc_payload)
            
            if payload.get('exp', 0) < time.time():
                raise InvalidCredentials("Token has expired.")

            return payload
        except Exception as e:
            if isinstance(e, InvalidCredentials):
                raise
            raise InvalidCredentials("Invalid token.") from e