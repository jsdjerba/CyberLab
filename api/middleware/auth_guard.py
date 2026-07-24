from functools import wraps
from flask import request, g, current_app
from domain.exceptions import ValidationError, InvalidCredentials, BaseDomainException

class AccessDenied(BaseDomainException):
    pass

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise InvalidCredentials("Missing or invalid Authorization header.")

        token = auth_header.split(' ')[1]
        
        # Le TokenManager doit être injecté dans l'app configuration au démarrage
        token_manager = current_app.config.get('TOKEN_MANAGER')
        if not token_manager:
            raise RuntimeError("TokenManager is not configured.")

        payload = token_manager.verify_token(token)
        g.user = payload  # Injection du contexte sécurisé
        
        return f(*args, **kwargs)
    return decorated

def require_role(role: str):
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_role(*args, **kwargs):
            if g.user.get('role') != role:
                raise AccessDenied(f"Access denied. Requires {role} role.")
            return f(*args, **kwargs)
        return decorated_role
    return decorator