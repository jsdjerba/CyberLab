"""Décorateur d'autorisation RBAC (Role-Based Access Control)."""
from functools import wraps
from presentation.security.security_exceptions import ForbiddenRoleException
from presentation.security.current_user import current_user

def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            allowed_values = [r.value for r in allowed_roles]
            if not current_user.role or current_user.role not in allowed_values:
                allowed_str = ", ".join(allowed_values)
                raise ForbiddenRoleException(f"Accès refusé. Rôles autorisés : {allowed_str}")
            return f(*args, **kwargs)
        return decorator
    return decorator