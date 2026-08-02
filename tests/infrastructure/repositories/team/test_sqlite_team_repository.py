# tests/infrastructure/repositories/team/test_sqlite_team_repository.py
import pytest
from datetime import datetime
from sqlalchemy.orm import sessionmaker

from domain.team.aggregate import Team
from domain.team.value_objects.team_id import TeamId
from domain.team.value_objects.classroom_id import ClassroomId
from domain.team.value_objects.team_color import TeamColor
from domain.team.entities.team_member import TeamMember
from domain.team.value_objects.student_id import StudentId
from domain.team.value_objects.team_role import TeamRole

from infrastructure.persistence.sqlite.database import create_sqlite_engine
from infrastructure.persistence.sqlite.models import Base, TeamModel, TeamMemberModel
from infrastructure.persistence.sqlite.team_repository import SqlAlchemyTeamRepository

@pytest.fixture
def sqlite_test_engine(tmp_path):
    db_path = tmp_path / "test_team_repo.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def sqlite_session(sqlite_test_engine):
    SessionMaker = sessionmaker(bind=sqlite_test_engine)
    session = SessionMaker()
    yield session
    session.close()

def test_find_team_hydrates_domain_aggregate(sqlite_session):
    team_model = TeamModel(
        id="team-1",
        classroom_id="class-1",
        color="RED",
        score=100,
        max_size=4,
        created_at=datetime(2026, 8, 2, 10, 0, 0),
        updated_at=datetime(2026, 8, 2, 10, 0, 0)
    )
    sqlite_session.add(team_model)
    sqlite_session.flush()

    member_model = TeamMemberModel(
        id="mem-1",
        team_id="team-1",
        student_id="student-1",
        role="CAPTAIN",
        joined_at=datetime(2026, 8, 2, 10, 0, 0)
    )
    sqlite_session.add(member_model)
    sqlite_session.commit()

    repo = SqlAlchemyTeamRepository(sqlite_session)
    team = repo.find_by_id("team-1")

    assert isinstance(team, Team)
    assert team.id.value == "team-1"
    assert team.classroom_id.value == "class-1"
    assert team.color == TeamColor.RED
    assert len(team.members) == 1
    assert len(team.pull_events()) == 0

def test_find_unknown_team_returns_none(sqlite_session):
    repo = SqlAlchemyTeamRepository(sqlite_session)
    team = repo.find_by_id("unknown-id")
    assert team is None

def test_save_new_team_persists(sqlite_session):
    team = Team.create(
        TeamId("team-new"),
        ClassroomId("class-1"),
        TeamColor.BLUE,
        5,
        datetime(2026, 8, 2, 12, 0, 0),
        "evt-1"
    )
    repo = SqlAlchemyTeamRepository(sqlite_session)
    repo.save(team)
    sqlite_session.commit()

    saved_model = sqlite_session.get(TeamModel, "team-new")
    assert saved_model is not None
    assert saved_model.classroom_id == "class-1"
    assert saved_model.color == "BLUE"

def test_save_updates_score(sqlite_session):
    team = Team.create(
        TeamId("team-score"),
        ClassroomId("class-1"),
        TeamColor.RED,
        3,
        datetime(2026, 8, 2, 12, 0, 0),
        "evt-2"
    )
    repo = SqlAlchemyTeamRepository(sqlite_session)
    repo.save(team)
    sqlite_session.commit()

    # Ingestion du paramètre obligatoire 'reason'
    team.award_points(
        points=50,
        reason="Victoire épreuve CTF",
        current_time=datetime(2026, 8, 2, 12, 30, 0),
        event_id="evt-3"
    )
    repo.save(team)
    sqlite_session.commit()

    saved_model = sqlite_session.get(TeamModel, "team-score")
    assert saved_model.score == 50

def test_save_members_correctly(sqlite_session):
    team = Team.create(
        TeamId("team-members"),
        ClassroomId("class-1"),
        TeamColor.RED,
        3,
        datetime(2026, 8, 2, 12, 0, 0),
        "evt-4"
    )
    team.add_member(
        student_id=StudentId("student-99"),
        role=TeamRole.CAPTAIN,
        current_time=datetime(2026, 8, 2, 12, 5, 0),
        event_id="evt-5"
    )
    repo = SqlAlchemyTeamRepository(sqlite_session)
    repo.save(team)
    sqlite_session.commit()

    count = sqlite_session.query(TeamMemberModel).filter_by(team_id="team-members").count()
    assert count == 1