import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from abc import ABC

@dataclass(frozen=True)
class DomainEvent(ABC):
    """Classe de base pour tous les événements métier."""
    # Générés automatiquement sans intervention du service producteur
    event_id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), init=False)