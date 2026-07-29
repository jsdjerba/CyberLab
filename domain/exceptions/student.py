"""
Exceptions liées à l'entité Étudiant (Student).
"""

from .base import BaseDomainException


class StudentNotFoundError(BaseDomainException):
    pass