"""Hiérarchie complète et typée des exceptions de sécurité (Remplacement des ValueError)."""

class SecurityError(Exception): """Base de toutes les exceptions de sécurité."""

# 1. Erreurs d'Authentification (Tokens)
class TokenError(SecurityError): pass
class MissingTokenError(TokenError): pass
class MalformedTokenError(TokenError): pass
class ExpiredTokenError(TokenError): pass
class InvalidTokenError(TokenError): pass
class SignatureVerificationError(TokenError): pass
class TokenRevokedError(TokenError): pass

# 2. Erreurs d'Autorisation (RBAC)
class AuthorizationError(SecurityError): pass
class ForbiddenRoleError(AuthorizationError): pass
class ForbiddenPermissionError(AuthorizationError): pass