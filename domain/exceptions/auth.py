"""
Exceptions liées au contexte d'authentification et d'identité.
"""

from .base import BaseDomainException


class UserAlreadyExists(BaseDomainException):
    pass


class InvalidCredentials(BaseDomainException):
    pass