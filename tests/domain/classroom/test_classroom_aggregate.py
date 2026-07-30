import pytest
from datetime import datetime, timedelta, timezone
from domain.value_objects.tenant_id import TenantId
from domain.value_objects.classroom_id import ClassroomId
from domain.value_objects.classroom_name import ClassroomName
from domain.value_objects.classroom_settings import ClassroomSettings
from domain.value_objects.teacher_id import TeacherId
from domain.value_objects.student_id import StudentId
from domain.value_objects.team_id import TeamId
from domain.value_objects.invitation_code import InvitationCode
from domain.enums.instructor_role import InstructorRole
from domain.enums.team_type import TeamType
from domain.entities.classroom import Classroom
from domain.exceptions.classroom_exceptions import *

def get_time(): return datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
def evt(n): return f"evt-{n}"

@pytest.fixture
def default_classroom():
    settings = ClassroomSettings(max_students=2, allow_team_switch=True, allow_multiple_teachers=False)
    return Classroom.create(TenantId("DEFAULT"), ClassroomId("c-1"), ClassroomName("CyberSec 101"), TeacherId("t-1"), settings, get_time(), evt(1), evt(2))

def test_classroom_creation_and_events(default_classroom):
    c = default_classroom
    assert c.version == 2 
    assert TeacherId("t-1") in c.instructors
    events = c.pull_events()
    assert len(events) == 2
    assert events[0].__class__.__name__ == "ClassroomCreated"
    assert events[0].occurred_at == get_time()
    assert events[0].event_id == evt(1)

def test_assign_second_primary_teacher_fails_if_not_allowed(default_classroom):
    c = default_classroom
    with pytest.raises(InstructorManagementException):
        c.assign_instructor(TeacherId("t-2"), InstructorRole.PRIMARY_TEACHER, get_time(), evt(3))

def test_assign_assistant_succeeds(default_classroom):
    c = default_classroom
    c.assign_instructor(TeacherId("t-2"), InstructorRole.ASSISTANT, get_time(), evt(3))
    assert TeacherId("t-2") in c.instructors
    assert c.version == 3

def test_generate_and_accept_invitation(default_classroom):
    c = default_classroom
    code = InvitationCode("SECURE22") 
    future = get_time() + timedelta(days=1)
    
    c.generate_invitation(code, future, get_time(), evt(3))
    c.accept_invitation(code, StudentId("s-1"), get_time(), evt(4), evt(5))
    
    assert StudentId("s-1") in c.members
    assert c.invitations[code].used_by == StudentId("s-1")
    assert c.version == 4

def test_accept_expired_invitation_fails(default_classroom):
    c = default_classroom
    code = InvitationCode("PASTDUE9") 
    past = get_time() - timedelta(days=1)
    c.generate_invitation(code, past, get_time(), evt(3))
    
    with pytest.raises(InvalidInvitationException):
        c.accept_invitation(code, StudentId("s-1"), get_time(), evt(4), evt(5))

def test_revoke_invitation_prevents_acceptance(default_classroom):
    c = default_classroom
    code = InvitationCode("REJECTED") 
    future = get_time() + timedelta(days=1)
    
    c.generate_invitation(code, future, get_time(), evt(3))
    c.revoke_invitation(code, get_time(), evt(4))
    
    with pytest.raises(InvalidInvitationException):
        c.accept_invitation(code, StudentId("s-1"), get_time(), evt(5), evt(6))

def test_capacity_is_strictly_enforced():
    settings = ClassroomSettings(max_students=1)
    c = Classroom.create(TenantId("DEFAULT"), ClassroomId("c-1"), ClassroomName("Micro Class"), TeacherId("t-1"), settings, get_time(), evt(1), evt(2))
    code = InvitationCode("MEGA2222") 
    c.generate_invitation(code, get_time() + timedelta(days=1), get_time(), evt(3))
    
    c.accept_invitation(code, StudentId("s-1"), get_time(), evt(4), evt(5))
    
    with pytest.raises(ClassroomCapacityExceededException):
        c.accept_invitation(code, StudentId("s-2"), get_time(), evt(6), evt(7))

def test_student_cannot_enroll_twice(default_classroom):
    c = default_classroom
    code = InvitationCode("ACCEPTME") 
    c.generate_invitation(code, get_time() + timedelta(days=1), get_time(), evt(3))
    
    c.accept_invitation(code, StudentId("s-1"), get_time(), evt(4), evt(5))
    with pytest.raises(StudentAlreadyEnrolledException):
        c.accept_invitation(code, StudentId("s-1"), get_time(), evt(6), evt(7))

def test_team_assignment_and_switch(default_classroom):
    c = default_classroom
    code = InvitationCode("ACCEPTME") 
    c.generate_invitation(code, get_time() + timedelta(days=1), get_time(), evt(3))
    c.accept_invitation(code, StudentId("s-1"), get_time(), evt(4), evt(5))
    
    c.create_team(TeamId("team-red"), "Red Team", TeamType.RED_TEAM, get_time(), evt(6))
    c.create_team(TeamId("team-blue"), "Blue Team", TeamType.BLUE_TEAM, get_time(), evt(7))
    
    c.assign_student_to_team(StudentId("s-1"), TeamId("team-red"), get_time(), evt(8))
    assert StudentId("s-1") in c.teams[TeamId("team-red")].members
    
    c.assign_student_to_team(StudentId("s-1"), TeamId("team-blue"), get_time(), evt(9))
    assert StudentId("s-1") not in c.teams[TeamId("team-red")].members
    assert StudentId("s-1") in c.teams[TeamId("team-blue")].members

def test_remove_student_cleans_up_teams(default_classroom):
    c = default_classroom
    code = InvitationCode("ACCEPTME") 
    c.generate_invitation(code, get_time() + timedelta(days=1), get_time(), evt(3))
    c.accept_invitation(code, StudentId("s-1"), get_time(), evt(4), evt(5))
    
    c.create_team(TeamId("team-red"), "Red Team", TeamType.RED_TEAM, get_time(), evt(6))
    c.assign_student_to_team(StudentId("s-1"), TeamId("team-red"), get_time(), evt(7))
    
    c.remove_student(StudentId("s-1"), get_time(), evt(8))
    
    assert StudentId("s-1") not in c.members
    assert StudentId("s-1") not in c.teams[TeamId("team-red")].members

def test_archived_classroom_is_immutable(default_classroom):
    c = default_classroom
    c.archive(get_time(), evt(3))
    
    with pytest.raises(ClassroomArchivedException):
        c.generate_invitation(InvitationCode("WHATEVER"), get_time(), get_time(), evt(4)) 

def test_invitation_code_ambiguous_chars_rejected():
    with pytest.raises(ValueError): InvitationCode("C0DE12")
    with pytest.raises(ValueError): InvitationCode("HELL0") 
    with pytest.raises(ValueError): InvitationCode("SHORT") 
    code = InvitationCode("cyber2") 
    assert code.value == "CYBER2"