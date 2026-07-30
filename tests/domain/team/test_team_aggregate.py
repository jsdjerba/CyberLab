import pytest
from datetime import datetime
from domain.team.aggregate import Team
from domain.team.value_objects.team_id import TeamId
from domain.team.value_objects.classroom_id import ClassroomId
from domain.team.value_objects.student_id import StudentId
from domain.team.value_objects.team_color import TeamColor
from domain.team.value_objects.team_role import TeamRole
from domain.team.exceptions.team_exceptions import (
    DuplicateTeamMemberException,
    TeamCapacityExceededException,
    CaptainAlreadyExistsException,
    NegativeScoreException
)
from domain.team.events.team_events import StudentAssignedToTeamEvent, PointsAwardedEvent

@pytest.fixture
def base_team():
    return Team.create(
        team_id=TeamId("team-1"),
        classroom_id=ClassroomId("class-1"),
        color=TeamColor.RED,
        max_size=3,
        current_time=datetime.now(),
        event_id="evt-1"
    )

def test_team_creation_initializes_zero_score(base_team):
    assert base_team.score.value == 0
    assert base_team.color == TeamColor.RED

def test_team_creation_has_empty_members(base_team):
    assert len(base_team.members) == 0

def test_add_member_success(base_team):
    now = datetime.now()
    base_team.add_member(StudentId("stu-1"), TeamRole.ATTACKER, now, "evt-2")
    
    assert len(base_team.members) == 1
    events = base_team.pull_events()
    assert any(isinstance(e, StudentAssignedToTeamEvent) for e in events)

def test_add_member_rejects_duplicate_student(base_team):
    now = datetime.now()
    base_team.add_member(StudentId("stu-1"), TeamRole.ATTACKER, now, "evt-2")
    with pytest.raises(DuplicateTeamMemberException):
        base_team.add_member(StudentId("stu-1"), TeamRole.DEFENDER, now, "evt-3")

def test_add_member_rejects_capacity_limit(base_team):
    now = datetime.now()
    base_team.add_member(StudentId("stu-1"), TeamRole.ATTACKER, now, "evt-1")
    base_team.add_member(StudentId("stu-2"), TeamRole.ATTACKER, now, "evt-2")
    base_team.add_member(StudentId("stu-3"), TeamRole.ATTACKER, now, "evt-3")
    
    with pytest.raises(TeamCapacityExceededException):
        base_team.add_member(StudentId("stu-4"), TeamRole.ATTACKER, now, "evt-4")

def test_assign_first_captain_success(base_team):
    now = datetime.now()
    base_team.add_member(StudentId("stu-1"), TeamRole.CAPTAIN, now, "evt-1")
    assert base_team.members[StudentId("stu-1")].role == TeamRole.CAPTAIN

def test_assign_second_captain_fails(base_team):
    now = datetime.now()
    base_team.add_member(StudentId("stu-1"), TeamRole.CAPTAIN, now, "evt-1")
    base_team.add_member(StudentId("stu-2"), TeamRole.ATTACKER, now, "evt-2")
    
    with pytest.raises(CaptainAlreadyExistsException):
        base_team.assign_role(StudentId("stu-2"), TeamRole.CAPTAIN, now, "evt-3")

def test_award_points_updates_score(base_team):
    now = datetime.now()
    base_team.award_points(50, "Flag Captured", now, "evt-1")
    assert base_team.score.value == 50

def test_award_points_emits_event(base_team):
    now = datetime.now()
    base_team.award_points(50, "Flag Captured", now, "evt-1")
    events = base_team.pull_events()
    award_event = next((e for e in events if isinstance(e, PointsAwardedEvent)), None)
    
    assert award_event is not None
    assert award_event.points == 50
    assert award_event.reason == "Flag Captured"

def test_deduct_points_prevents_negative_score(base_team):
    now = datetime.now()
    base_team.award_points(10, "Initial", now, "evt-1")
    with pytest.raises(NegativeScoreException):
        base_team.deduct_points(20, "Penalty", now, "evt-2")

def test_pull_events_clears_buffer(base_team):
    assert len(base_team.pull_events()) == 1  # TeamCreatedEvent
    assert len(base_team.pull_events()) == 0  # Buffer is now empty