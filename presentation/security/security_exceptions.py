"""Exceptions spécifiques à la couche présentation (HTTP Sécurité)."""

class SecurityException(Exception): pass
class MissingTokenException(SecurityException): pass
class ExpiredTokenException(SecurityException): pass
class InvalidTokenException(SecurityException): pass
class ForbiddenRoleException(SecurityException): pass