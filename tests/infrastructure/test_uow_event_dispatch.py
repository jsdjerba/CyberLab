import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.base import Base
from infrastructure.persistence.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from domain.common.aggregate_root import AggregateRoot
from application.ports.event_bus import AbstractEventBus

class FakeEventBus(AbstractEventBus):
    def __init__(self):
        self.published_events = []

    def subscribe(self, event_type, handler) -> None:
        pass

    def publish(self, event) -> None:
        self.published_events.append(event)

class DummyAggregateRoot(AggregateRoot):
    def __init__(self):
        super().__init__()
        self.name = "Test"

@pytest.fixture
def sqlite_uow_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    return session_maker

def test_uow_collects_and_publishes_events_on_commit(sqlite_uow_factory):
    event_bus = FakeEventBus()
    uow = SqlAlchemyUnitOfWork(sqlite_uow_factory, event_bus=event_bus)

    aggregate = DummyAggregateRoot()
    aggregate.register_event("EventCommitted")

    with uow:
        uow.register_aggregate(aggregate)
        uow.commit()

    assert len(event_bus.published_events) == 1
    assert event_bus.published_events[0] == "EventCommitted"

def test_uow_does_not_publish_events_on_rollback(sqlite_uow_factory):
    event_bus = FakeEventBus()
    uow = SqlAlchemyUnitOfWork(sqlite_uow_factory, event_bus=event_bus)

    aggregate = DummyAggregateRoot()
    aggregate.register_event("EventRollbacked")

    with pytest.raises(RuntimeError):
        with uow:
            uow.register_aggregate(aggregate)
            raise RuntimeError("Forced Rollback")

    assert len(event_bus.published_events) == 0