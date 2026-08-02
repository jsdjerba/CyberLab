from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from infrastructure.persistence.sqlite.outbox_model import OutboxEventModel

class SqlAlchemyOutboxRepository:
    """
    Adaptateur Infrastructure pour la persistance des Domain Events via l'Outbox.
    """
    def __init__(self, session: Session):
        self._session = session

    def save(
        self,
        event_id: str,
        aggregate_type: str,
        aggregate_id: str,
        event_type: str,
        event_version: int,
        payload: str,
        occurred_at: datetime
    ) -> None:
        model = OutboxEventModel(
            id=event_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            event_version=event_version,
            payload=payload,
            occurred_at=occurred_at,
            processed_at=None
        )
        self._session.add(model)

    def mark_processed(self, event_id: str, processed_at: datetime) -> None:
        model = self._session.get(OutboxEventModel, event_id)
        if model:
            model.processed_at = processed_at

    def find_unprocessed(self) -> List[OutboxEventModel]:
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.processed_at.is_(None))
            .order_by(OutboxEventModel.occurred_at.asc())
        )
        return list(self._session.execute(stmt).scalars().all())