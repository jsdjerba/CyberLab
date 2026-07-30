"""Encapsulation stricte du AuthContext."""
from flask import g
from application.dto.auth_context import AuthContext

class CurrentUser:
    @property
    def _context(self) -> AuthContext:
        if not hasattr(g, 'auth'):
            raise RuntimeError("Tentative d'accès à CurrentUser hors d'un contexte sécurisé.")
        return g.auth

    @property
    def id(self) -> str: return self._context.user_id

    @property
    def roles(self) -> list: return self._context.roles

    @property
    def permissions(self) -> list: return self._context.permissions

current_user = CurrentUser()