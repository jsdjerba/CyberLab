from sqlalchemy.orm import Session
from application.ports.audit_repository import AuditRepository
from domain.entities.audit_event import AuditEvent
from infrastructure.persistence.models.audit_model import AuditEventModel

class SqlAlchemyAuditRepository(AuditRepository):
    def __init__(self, session: Session):
        self._session = session

    def save(self, event: AuditEvent) -> None:
        model = AuditEventModel(
            event_id=event.event_id,
            timestamp=event.timestamp,
            action=event.action,
            status=event.status,
            user_id=event.user_id,
            details=event.details,
            ip_address=event.ip_address
        )
        self._session.add(model)
        self._session.commit()