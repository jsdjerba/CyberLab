"""
Exceptions liées au suivi de progression (Progress Context).
"""

from .base import BaseDomainException


class InvalidProgressTransitionError(BaseDomainException):
    pass


class LabAlreadyCompletedError(BaseDomainException):
    """
    Note architecturale : Conservé pour compatibilité avec l'ancien système.
    Le nouveau système (LabInstance) utilise LabAlreadyCompletedException.
    """
    pass


# Alias de rétrocompatibilité pour l'API historique
ProgressAlreadyCompleted = LabAlreadyCompletedError