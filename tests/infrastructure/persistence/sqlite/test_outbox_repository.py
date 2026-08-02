import pytest
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from infrastructure.persistence.sqlite.database import create_sqlite_engine
from infrastructure.persistence.sqlite.models import Base
# IMPORTS ANTICIPÉS POUR PROVOQUER LE RED STATE
from infrastructure.persistence.sqlite.outbox_repository import SqlAlchemyOutboxRepository
from infrastructure.persistence.sqlite.outbox_model import OutboxEventModel

@pytest.fixture
def sqlite_session(tmp_path):
    db_path = tmp_path / "test_outbox_repo.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    SessionMaker = sessionmaker(bind=engine)
    session = SessionMaker()
    yield session
    session.close()

def test_save_single_event(sqlite_session):
    """Vérifie qu'un événement unique peut être sauvegardé via l'outbox repository."""
    repo = SqlAlchemyOutboxRepository(sqlite_session)
    repo.save(
        event_id="evt-1",
        aggregate_type="Team",
        aggregate_id="team-1",
        event_type="PointsAwardedEvent",
        event_version=1,
        payload='{"points": 10}',
        occurred_at=datetime(2026, 8, 2, 16, 0, 0)
    )
    sqlite_session.commit()

    saved = sqlite_session.get(OutboxEventModel, "evt-1")
    assert saved is not None
    assert saved.event_type == "PointsAwardedEvent"
    assert saved.processed_at is None

def test_save_multiple_events(sqlite_session):
    """Vérifie la sauvegarde de plusieurs événements en une seule passe."""
    repo = SqlAlchemyOutboxRepository(sqlite_session)
    repo.save("evt-1", "Team", "t-1", "EventA", 1, "{}", datetime.now())
    repo.save("evt-2", "Team", "t-1", "EventB", 1, "{}", datetime.now())
    sqlite_session.commit()

    count = sqlite_session.query(OutboxEventModel).count()
    assert count == 2

def test_events_keep_order(sqlite_session):
    """Vérifie que l'ordre chronologique des événements est préservé à la lecture."""
    repo = SqlAlchemyOutboxRepository(sqlite_session)
    t1 = datetime(2026, 8, 2, 10, 0, 0)
    t2 = datetime(2026, 8, 2, 11, 0, 0)
    repo.save("evt-1", "Team", "t-1", "EventA", 1, "{}", t1)
    repo.save("evt-2", "Team", "t-1", "EventB", 1, "{}", t2)
    sqlite_session.commit()

    events = repo.find_unprocessed()
    assert events[0].id == "evt-1"
    assert events[1].id == "evt-2"

def test_mark_event_processed(sqlite_session):
    """Vérifie qu'un événement peut être marqué comme traité (processed_at renseigné)."""
    repo = SqlAlchemyOutboxRepository(sqlite_session)
    repo.save("evt-1", "Team", "t-1", "EventA", 1, "{}", datetime.now())
    sqlite_session.commit()

    repo.mark_processed("evt-1", datetime.now())
    sqlite_session.commit()

    event = sqlite_session.get(OutboxEventModel, "evt-1")
    assert event.processed_at is not None

def test_find_unprocessed_events(sqlite_session):
    """Vérifie que seuls les événements non traités sont retournés."""
    repo = SqlAlchemyOutboxRepository(sqlite_session)
    repo.save("evt-1", "Team", "t-1", "EventA", 1, "{}", datetime.now())
    repo.save("evt-2", "Team", "t-1", "EventB", 1, "{}", datetime.now())
    sqlite_session.commit()

    repo.mark_processed("evt-1", datetime.now())
    sqlite_session.commit()

    unprocessed = repo.find_unprocessed()
    assert len(unprocessed) == 1
    assert unprocessed[0].id == "evt-2"

def test_processed_events_not_returned(sqlite_session):
    """Vérifie qu'aucun événement déjà traité n'apparaît dans find_unprocessed."""
    repo = SqlAlchemyOutboxRepository(sqlite_session)
    repo.save("evt-1", "Team", "t-1", "EventA", 1, "{}", datetime.now())
    repo.mark_processed("evt-1", datetime.now())
    sqlite_session.commit()

    assert len(repo.find_unprocessed()) == 0