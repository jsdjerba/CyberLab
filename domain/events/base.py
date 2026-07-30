"""
Classe de base pour tous les événements de domaine de l'application.
Garantit une interface commune pour l'Event Bus (Unit of Work).
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class BaseDomainEvent:
    """
    Marqueur abstrait pour les événements de domaine.
    Toutes les classes d'événements (UserRegistered, LabStarted, etc.) doivent en hériter.
    """
    pass