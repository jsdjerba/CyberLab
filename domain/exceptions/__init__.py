"""
Façade exposant l'ensemble des exceptions du domaine.
Garantit la rétrocompatibilité stricte avec les imports existants
tout en maintenant une architecture modulaire sous-jacente.
"""

from .base import BaseDomainException
from .auth import UserAlreadyExists, InvalidCredentials
from .validation import ValidationError, InvalidFlag
from .student import StudentNotFoundError
from .lab import (
    LabNotFoundError,
    LabNotFound,
    LabInstanceNotFoundError,
    LabNotStartedException,
    LabAlreadyCompletedException,
    LabLockedOutException,
    CooldownException,
    InvalidLabStateException
)
from .progress import (
    InvalidProgressTransitionError,
    LabAlreadyCompletedError,
    ProgressAlreadyCompleted
)

__all__ = [
    "BaseDomainException",
    "UserAlreadyExists",
    "InvalidCredentials",
    "ValidationError",
    "InvalidFlag",
    "StudentNotFoundError",
    "LabNotFoundError",
    "LabNotFound",
    "LabInstanceNotFoundError",
    "LabNotStartedException",
    "LabAlreadyCompletedException",
    "LabLockedOutException",
    "CooldownException",
    "InvalidLabStateException",
    "InvalidProgressTransitionError",
    "LabAlreadyCompletedError",
    "ProgressAlreadyCompleted"
]