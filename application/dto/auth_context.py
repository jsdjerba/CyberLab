"""Contexte de sécurité déchiffré et validé. Indépendant de Flask."""
from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass(frozen=True)
class AuthContext:
    user_id: str
    roles: List[str]
    permissions: List[str]
    claims: dict
    token_id: str
    issued_at: datetime
    expires_at: datetime
    
    def has_role(self, role: str) -> bool:
        return role in self.roles
        
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions