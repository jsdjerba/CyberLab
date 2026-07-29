"""
Exceptions liées à la validation des données et des formats métier.
"""

from .base import BaseDomainException


class ValidationError(BaseDomainException):
    pass


# Alias de rétrocompatibilité stricte pour l'API historique
InvalidFlag = ValidationError