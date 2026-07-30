"""
Orchestrateur central de sécurité.
Protège la pureté de la couche HTTP en encapsulant toute la complexité JWT et BDD.
"""
from typing import List, Optional
from application.dto.auth_context import AuthContext
from application.ports.token_provider import TokenProvider
from application.ports.user_repository import UserRepository
from application.ports.audit_repository import AuditRepository
from domain.entities.audit_event import AuditEvent
from application.exceptions.security_exceptions import (
    MissingTokenError, MalformedTokenError, TokenRevokedError,
    ForbiddenRoleError, ForbiddenPermissionError
)

class SecurityService:
    def __init__(
        self, 
        token_provider: TokenProvider, 
        user_repository: UserRepository,
        audit_repository: AuditRepository
    ):
        self._token_provider = token_provider
        self._user_repository = user_repository
        self._audit_repository = audit_repository

    def verify_request(self, auth_header: Optional[str], ip_address: str = "unknown") -> AuthContext:
        """Décode, vérifie la révocation et construit le contexte."""
        if not auth_header:
            raise MissingTokenError("Token JWT manquant.")
            
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise MalformedTokenError("Format d'en-tête Authorization invalide. Attendu: Bearer <token>")
            
        token = parts[1]
        
        # Le TokenProvider lève ExpiredTokenError ou InvalidTokenError (typés)
        payload = self._token_provider.decode_token(token)
        
        # RÉVOCATION IMMÉDIATE (Sécurité Enterprise pour Raspberry Pi)
        user = self._user_repository.find_by_id(payload.user_id)
        if not user or not user.is_active:
            self._audit_repository.save(AuditEvent("TOKEN_USE", "DENIED", payload.user_id, "Utilisateur inactif ou supprimé", ip_address))
            raise TokenRevokedError("Compte utilisateur désactivé. Jeton révoqué.")
            
        # Construction du AuthContext
        return AuthContext(
            user_id=payload.user_id,
            roles=[user.role.value],
            permissions=[p.value for p in user.role.permissions],
            claims={"iss": "cyberlab", "aud": "cyberlab-api"},
            token_id=payload.claims.get("jti", "unknown"),
            issued_at=payload.issued_at,
            expires_at=payload.expiration
        )

    def enforce_role(self, context: AuthContext, allowed_roles: List[str], ip_address: str = "unknown"):
        if not any(context.has_role(r) for r in allowed_roles):
            self._audit_repository.save(AuditEvent("ACCESS", "DENIED", context.user_id, f"Manque rôle(s) parmi: {allowed_roles}", ip_address))
            raise ForbiddenRoleError(f"Rôle insuffisant. Requis : {allowed_roles}")

    def enforce_permission(self, context: AuthContext, allowed_permissions: List[str], ip_address: str = "unknown"):
        if not any(context.has_permission(p) for p in allowed_permissions):
            self._audit_repository.save(AuditEvent("ACCESS", "DENIED", context.user_id, f"Manque permission: {allowed_permissions}", ip_address))
            raise ForbiddenPermissionError(f"Permission refusée. Requise : {allowed_permissions}")