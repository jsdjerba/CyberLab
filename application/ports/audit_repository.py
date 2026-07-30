from typing import Protocol
from domain.entities.audit_event import AuditEvent

class AuditRepository(Protocol):
    def save(self, event: AuditEvent) -> None: ...