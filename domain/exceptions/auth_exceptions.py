"""
Exceptions métier liées à l'authentification et l'autorisation.
"""
from domain.exceptions.base import BaseDomainException # Assumant l'existence d'une exception de base

class DuplicateUserException(BaseDomainException):
    pass

class UserNotFoundException(BaseDomainException):
    pass

class InvalidPasswordException(BaseDomainException):
    pass

class AuthenticationError(BaseDomainException):
    pass