from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class DomainEvent(ABC):
    # L'utilisation de kw_only (disponible en Python 3.10+) évite les conflits d'héritage avec les champs sans valeur par défaut
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)

@dataclass(frozen=True)
class LabStarted(DomainEvent):
    instance_id: str
    lab_id: Any

@dataclass(frozen=True)
class StepCompleted(DomainEvent):
    instance_id: str
    step_id: Any

@dataclass(frozen=True)
class LabFinished(DomainEvent):
    instance_id: str
    final_score: Any