"""
Décorateurs HTTP élégants et dépouillés.
Ils ne font que déléguer au SecurityService (Inversion de Dépendances).
"""
from functools import wraps
from flask import request, g, current_app
from domain.value_objects.role import Role
from domain.value_objects.permission import Permission

def _get_security_service():
    """Récupère l'interface publique du service depuis le conteneur."""
    return current_app.container.security_service

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        service = _get_security_service()
        ip = request.remote_addr or "unknown"
        # Le service s'occupe de TOUT (validation, décodage, check BDD, génération context)
        g.auth = service.verify_request(request.headers.get("Authorization"), ip_address=ip)
        return f(*args, **kwargs)
    return decorated_function

def require_role(*allowed_roles: Role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            service = _get_security_service()
            roles_str = [r.value for r in allowed_roles]
            service.enforce_role(g.auth, roles_str, request.remote_addr or "unknown")
            return f(*args, **kwargs)
        return decorated_function # CORRIGÉ : Retourne la fonction décorée
    return decorator

def require_permission(*allowed_permissions: Permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            service = _get_security_service()
            perms_str = [p.value for p in allowed_permissions]
            service.enforce_permission(g.auth, perms_str, request.remote_addr or "unknown")
            return f(*args, **kwargs)
        return decorated_function # CORRIGÉ : Retourne la fonction décorée
    return decorator