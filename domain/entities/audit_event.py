"""Entité du Domaine représentant un journal de sécurité immutable (Accounting)."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(frozen=True)
class AuditEvent:
    action: str
    status: str # SUCCESS, FAILED, DENIED
    user_id: str
    details: str
    ip_address: str = "unknown"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:12]}")