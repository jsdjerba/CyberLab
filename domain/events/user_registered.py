"""Événement émis lors de l'inscription d'un nouvel utilisateur."""
from dataclasses import dataclass
from datetime import datetime
from domain.events.base import BaseDomainEvent  # Import de l'existant

@dataclass(frozen=True)
class UserRegistered(BaseDomainEvent):
    user_id: str
    email: str
    role: str
    timestamp: datetime