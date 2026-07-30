"""Décorateur d'authentification interceptant et validant le JWT."""
from functools import wraps
from flask import request, g, current_app
from presentation.security.security_exceptions import (
    MissingTokenException, InvalidTokenException, ExpiredTokenException
)

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise MissingTokenException("Token JWT manquant ou mal formaté.")

        token = auth_header.split(" ")[1]
        # Extraction via le conteneur d'injection de dépendances
        provider = current_app.container._token_provider 

        try:
            payload = provider.decode_token(token)
            g.user_id = payload.user_id
            g.role = payload.role
            g.token_payload = payload
        except ValueError as e:
            if "expiré" in str(e).lower():
                raise ExpiredTokenException("Le token a expiré.")
            raise InvalidTokenException("Token invalide ou corrompu.")

        return f(*args, **kwargs)
    return decorated_function