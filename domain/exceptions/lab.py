"""
Exceptions liées au contexte d'exécution des laboratoires (Lab Range).
"""

from .base import BaseDomainException


class LabNotFoundError(BaseDomainException):
    pass


# Alias de rétrocompatibilité stricte pour les anciens handlers d'API
LabNotFound = LabNotFoundError


class LabInstanceNotFoundError(BaseDomainException):
    pass


class LabNotStartedException(BaseDomainException):
    pass


class LabAlreadyCompletedException(BaseDomainException):
    pass


class LabLockedOutException(BaseDomainException):
    pass


class CooldownException(BaseDomainException):
    pass


class InvalidLabStateException(BaseDomainException):
    pass