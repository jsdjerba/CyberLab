"""Événement émis lors d'une connexion réussie."""
from dataclasses import dataclass
from datetime import datetime
from domain.events.base import BaseDomainEvent  # Import de l'existant

@dataclass(frozen=True)
class UserLoggedIn(BaseDomainEvent):
    user_id: str
    timestamp: datetime