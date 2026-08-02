from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Index
from infrastructure.persistence.sqlite.models import Base

class OutboxEventModel(Base):
    """
    Modèle physique SQLAlchemy représentant un événement dans l'Outbox.
    Conforme au pattern Transactional Outbox pour SQLite WAL.
    """
    __tablename__ = "outbox_events"

    id = Column(String, primary_key=True)
    aggregate_type = Column(String, nullable=False)
    aggregate_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    event_version = Column(Integer, nullable=False, default=1)
    payload = Column(Text, nullable=False)
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

# Index partiel SQLite pour cibler instantanément les événements non traités (processed_at IS NULL)
Index(
    "idx_outbox_unprocessed",
    OutboxEventModel.processed_at,
    sqlite_where=(OutboxEventModel.processed_at == None)
)