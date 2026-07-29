"""
Module regroupant les exceptions purement métier (Domain Exceptions) du Learning Context.
Ces exceptions garantissent que les violations des règles métier sont signalées
sans fuite d'abstraction technologique (ni HTTP, ni SQL).
"""

class DomainException(Exception):
    """
    Classe de base pour toutes les exceptions du domaine CyberLab.
    Permet à la couche Application (Use Cases) d'intercepter globalement les erreurs métier.
    """
    pass


class LabNotStartedException(DomainException):
    """
    Levée lorsqu'une action nécessitant un laboratoire actif est entreprise
    alors que le statut est encore NOT_STARTED.
    """
    pass


class LabAlreadyCompletedException(DomainException):
    """
    Levée lorsqu'une mutation est tentée sur un laboratoire dont
    le statut est déjà COMPLETED, garantissant son immuabilité finale.
    """
    pass


class LabLockedOutException(DomainException):
    """
    Levée lorsque l'AttemptPolicy détermine que l'étudiant a dépassé
    le nombre maximum de tentatives autorisées. Représente le mécanisme anti-bruteforce.
    """
    pass


class CooldownException(DomainException):
    """
    Levée lorsque l'AttemptPolicy bloque une tentative car le délai de 
    refroidissement (cooldown) entre deux essais n'est pas respecté.
    """
    pass


class InvalidLabStateException(DomainException):
    """
    Levée lorsqu'une transition d'état impossible ou non gérée 
    est demandée à la machine à états de LabInstance.
    """
    pass