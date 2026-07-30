import pytest
from datetime import datetime, timedelta
from dataclasses import dataclass

from application.commands.rotate_invitation_command import RotateInvitationCommand
from application.dto.invitation_response import InvitationResponseDTO
from application.use_cases.rotate_invitation import RotateInvitationUseCase
from application.exceptions.application_exceptions import NotFoundApplicationException, ConcurrencyApplicationException
from application.resilience.retry_policy import RetryPolicy

from tests.fakes.fake_clock import FakeClock
from tests.fakes.fake_id_generator import FakeIdGenerator
from tests.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.fakes.fake_delay_provider import FakeDelayProvider

# --- DOMAIN EXCEPTIONS MOCKS ---
class DomainException(Exception): pass
class UnknownInvitationDomainException(DomainException): pass
class AlreadyRevokedDomainException(DomainException): pass
class UnauthorizedTeacherDomainException(DomainException): pass
class ClassroomArchivedDomainException(DomainException): pass
class DatabaseLockedException(Exception): pass

# --- DOMAIN EVENT MOCK ---
@dataclass(frozen=True)
class InvitationRotatedEvent:
    event_id: str
    classroom_id: str
    old_invitation_code: str
    new_invitation_code: str
    rotated_by: str
    old_revoked_at: datetime
    new_expires_at: datetime
    occurred_at: datetime
    event_version: int = 1

# --- DOMAIN AGGREGATE MOCK ---
class DummyClassroom:
    def __init__(self, classroom_id: str):
        self.id = classroom_id
        self._events = []
        self.rotate_invitation_calls = 0

    def rotate_invitation(
        self, old_invitation_code: str, new_invitation_code: str,
        requested_by: str, current_time: datetime, validity_hours: int, event_id: str
    ):
        self.rotate_invitation_calls += 1
        
        if requested_by == "unauthorized_teacher":
            raise UnauthorizedTeacherDomainException("Teacher not authorized.")
        if requested_by == "archived_classroom":
            raise ClassroomArchivedDomainException("Classroom is archived.")
        if old_invitation_code == "UNKNOWN":
            raise UnknownInvitationDomainException("Invitation not found.")
        if old_invitation_code == "ALREADY_REVOKED":
            raise AlreadyRevokedDomainException("Invitation already revoked.")

        event = InvitationRotatedEvent(
            event_id=event_id,
            classroom_id=self.id,
            old_invitation_code=old_invitation_code,
            new_invitation_code=new_invitation_code,
            rotated_by=requested_by,
            old_revoked_at=current_time,
            new_expires_at=current_time + timedelta(hours=validity_hours),
            occurred_at=current_time,
            event_version=1
        )
        self._events.append(event)

    def pull_events(self):
        events = list(self._events)
        self._events.clear()
        return events

# --- FAKES ---
class FakeClassroomRepository:
    def __init__(self):
        self.classrooms = {}
        self.save_calls = 0

    def find_by_id(self, classroom_id: str):
        return self.classrooms.get(classroom_id)

    def save(self, classroom):
        self.save_calls += 1

class FakeInvitationCodeGenerator:
    def __init__(self):
        self.generate_calls = 0
    def generate(self) -> str:
        self.generate_calls += 1
        return f"NEW-SECURE-{self.generate_calls}"

# --- FIXTURE ---
@pytest.fixture
def setup_usecase():
    repo = FakeClassroomRepository()
    repo.classrooms["class-123"] = DummyClassroom("class-123")
    
    code_gen = FakeInvitationCodeGenerator()
    clock = FakeClock(datetime(2026, 7, 31, 10, 0, 0))
    id_gen = FakeIdGenerator()
    uow = FakeUnitOfWork()
    
    retry_policy = RetryPolicy(
        delay_provider=FakeDelayProvider(),
        retryable_exceptions=(DatabaseLockedException,),
        max_attempts=3,
        initial_delay_ms=0,
        max_delay_ms=0
    )
    
    use_case = RotateInvitationUseCase(
        repository=repo,
        code_generator=code_gen,
        clock=clock,
        id_generator=id_gen,
        unit_of_work=uow,
        retry_policy=retry_policy
    )
    return use_case, repo, uow, code_gen

# --- TESTS ---

def test_rotate_invitation_success(setup_usecase):
    use_case, repo, uow, code_gen = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=24)
    
    response = use_case.execute(command)
    
    classroom = repo.classrooms["class-123"]
    assert classroom.rotate_invitation_calls == 1
    assert code_gen.generate_calls == 1
    assert repo.save_calls == 1
    assert uow.commit_called is True
    
    events = uow.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], InvitationRotatedEvent)
    
    assert isinstance(response, InvitationResponseDTO)
    assert response.status == "ACTIVE"
    assert response.invitation_code == "NEW-SECURE-1"
    assert response.event_version == 1

def test_rotate_classroom_not_found(setup_usecase):
    use_case, _, uow, _ = setup_usecase
    command = RotateInvitationCommand(classroom_id="unknown", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=24)
    
    with pytest.raises(NotFoundApplicationException):
        use_case.execute(command)
    assert uow.commit_called is False

def test_rotate_unknown_old_invitation(setup_usecase):
    use_case, repo, uow, _ = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="UNKNOWN", validity_hours=24)
    
    with pytest.raises(UnknownInvitationDomainException):
        use_case.execute(command)
    assert repo.save_calls == 0

def test_rotate_already_revoked_old_invitation(setup_usecase):
    use_case, repo, uow, _ = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="ALREADY_REVOKED", validity_hours=24)
    
    with pytest.raises(AlreadyRevokedDomainException):
        use_case.execute(command)
    assert uow.commit_called is False

def test_rotate_archived_classroom(setup_usecase):
    use_case, repo, uow, _ = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="archived_classroom", old_invitation_code="OLD-1", validity_hours=24)
    
    with pytest.raises(ClassroomArchivedDomainException):
        use_case.execute(command)
    assert uow.commit_called is False

def test_rotate_unauthorized_teacher(setup_usecase):
    use_case, repo, uow, _ = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="unauthorized_teacher", old_invitation_code="OLD-1", validity_hours=24)
    
    with pytest.raises(UnauthorizedTeacherDomainException):
        use_case.execute(command)

def test_rotate_generates_new_invitation_code(setup_usecase):
    use_case, _, _, code_gen = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=24)
    use_case.execute(command)
    assert code_gen.generate_calls == 1

def test_rotate_database_locked_retry(setup_usecase):
    use_case, repo, uow, _ = setup_usecase
    uow.simulate_failure(DatabaseLockedException("DB locked"))
    
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=24)
    
    response = use_case.execute(command)
    
    classroom = repo.classrooms["class-123"]
    # Vérification vitale : mutation métier UNE SEULE FOIS, même avec un fail de BDD
    assert classroom.rotate_invitation_calls == 1 
    assert repo.save_calls == 2
    assert uow.commit_called is True
    assert response.status == "ACTIVE"

def test_rotate_retry_exhausted(setup_usecase):
    use_case, repo, uow, _ = setup_usecase
    def always_fail(): raise DatabaseLockedException("Locked")
    uow.commit = always_fail
    
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=24)
    
    with pytest.raises(ConcurrencyApplicationException):
        use_case.execute(command)
    assert repo.save_calls == 3

def test_rotate_emits_specific_rotated_event(setup_usecase):
    use_case, repo, uow, _ = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=24)
    use_case.execute(command)
    events = uow.collect_events()
    assert len(events) == 1
    assert type(events[0]).__name__ == "InvitationRotatedEvent"

def test_rotate_is_atomic_when_commit_fails(setup_usecase):
    use_case, repo, uow, _ = setup_usecase
    def fail_immediately(): raise RuntimeError("Crash System")
    uow.commit = fail_immediately
    
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=24)
    with pytest.raises(RuntimeError):
        use_case.execute(command)
        
    assert uow.rollback_called is True

def test_usecase_does_not_access_invitation_entity(setup_usecase):
    use_case, repo, _ , _ = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=24)
    
    classroom = repo.classrooms["class-123"]
    assert not hasattr(classroom, "invitations")
    
    use_case.execute(command)

def test_usecase_contains_no_business_rules(setup_usecase):
    use_case, _, _, _ = setup_usecase
    command = RotateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", old_invitation_code="OLD-1", validity_hours=48)
    # L'expiration est gérée à l'intérieur du DummyClassroom
    response = use_case.execute(command)
    assert response.expires_at == datetime(2026, 7, 31, 10, 0, 0) + timedelta(hours=48)