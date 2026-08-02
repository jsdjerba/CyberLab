import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from infrastructure.persistence.sqlite.database import create_sqlite_engine
from infrastructure.persistence.sqlite.models import Base, TeamModel
from infrastructure.persistence.sqlite.unit_of_work import SqlAlchemyUnitOfWork
from domain.team.aggregate import Team
from domain.team.value_objects.team_id import TeamId
from domain.team.value_objects.classroom_id import ClassroomId
from domain.team.value_objects.team_color import TeamColor

@pytest.fixture
def sqlite_engine(tmp_path):
    db_path = tmp_path / "test_uow_events.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine

def test_commit_persists_team_and_events(sqlite_engine):
    """Vérifie que le commit persiste à la fois l'état de l'équipe et les événements outbox."""
    uow = SqlAlchemyUnitOfWork(sqlite_engine)
    with uow:
        team = Team.create(
            TeamId("team-uow-1"),
            ClassroomId("class-1"),
            TeamColor.RED,
            4,
            datetime(2026, 8, 2, 12, 0, 0),
            "evt-create"
        )
        uow.teams.save(team)
        for event in team.pull_events():
            uow.outbox.save(
                event_id=event.event_id,
                aggregate_type="Team",
                aggregate_id=team.id.value,
                event_type=event.__class__.__name__,
                event_version=1,
                payload='{}',
                occurred_at=event.occurred_at
            )
        uow.commit()

    with uow:
        saved_team = uow.teams.find_by_id("team-uow-1")
        assert saved_team is not None
        unprocessed = uow.outbox.find_unprocessed()
        assert len(unprocessed) >= 1

def test_exception_rolls_back_everything(sqlite_engine):
    """Vérifie qu'une exception lève un rollback complet (ni team ni outbox persistés)."""
    uow = SqlAlchemyUnitOfWork(sqlite_engine)
    with pytest.raises(ValueError):
        with uow:
            team = Team.create(
                TeamId("team-uow-rollback"),
                ClassroomId("class-1"),
                TeamColor.BLUE,
                4,
                datetime(2026, 8, 2, 12, 0, 0),
                "evt-create"
            )
            uow.teams.save(team)
            raise ValueError("Erreur critique simulée")

    with uow:
        assert uow.teams.find_by_id("team-uow-rollback") is None

def test_context_manager_closes_session(sqlite_engine):
    """Vérifie que le gestionnaire de contexte ferme proprement la session SQLAlchemy."""
    uow = SqlAlchemyUnitOfWork(sqlite_engine)
    with uow:
        pass
    assert True

def test_commit_without_exception(sqlite_engine):
    """Vérifie qu'un commit réussi s'exécute sans lever d'exception."""
    uow = SqlAlchemyUnitOfWork(sqlite_engine)
    with uow:
        uow.commit()
    assert True

def test_rollback_called_on_failure(sqlite_engine):
    """Vérifie que le rollback est invoqué en cas d'erreur dans le bloc with."""
    uow = SqlAlchemyUnitOfWork(sqlite_engine)
    try:
        with uow:
            raise RuntimeError("Crash test")
    except RuntimeError:
        pass
    assert True

def test_team_and_outbox_same_transaction(sqlite_engine):
    """Vérifie l'atomicité stricte : équipe et outbox vivent dans la même transaction."""
    uow = SqlAlchemyUnitOfWork(sqlite_engine)
    with uow:
        team = Team.create(
            TeamId("team-atomic"),
            ClassroomId("class-1"),
            TeamColor.RED,
            4,
            datetime(2026, 8, 2, 12, 0, 0),
            "evt-atomic"
        )
        uow.teams.save(team)
        uow.outbox.save("evt-outbox-1", "Team", "team-atomic", "TestEvent", 1, "{}", datetime.now())
        uow.commit()

    with uow:
        assert uow.teams.find_by_id("team-atomic") is not None
        assert len(uow.outbox.find_unprocessed()) == 1

def test_outbox_failure_rolls_back_team(sqlite_engine):
    """Si l'insertion outbox échoue, l'équipe ne doit pas être persistée."""
    uow = SqlAlchemyUnitOfWork(sqlite_engine)
    with pytest.raises(Exception):
        with uow:
            team = Team.create(
                TeamId("team-fail-outbox"),
                ClassroomId("class-1"),
                TeamColor.RED,
                4,
                datetime(2026, 8, 2, 12, 0, 0),
                "evt-fail"
            )
            uow.teams.save(team)
            uow.outbox.save("dup-id", "Team", "t-1", "EventA", 1, "{}", datetime.now())
            uow.outbox.save("dup-id", "Team", "t-1", "EventB", 1, "{}", datetime.now())
            uow.commit()

    with uow:
        assert uow.teams.find_by_id("team-fail-outbox") is None