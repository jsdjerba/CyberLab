import pytest
from datetime import datetime, timedelta
from dataclasses import dataclass

from application.commands.revoke_invitation_command import RevokeInvitationCommand
from application.dto.invitation_response import InvitationResponseDTO
from application.use_cases.revoke_invitation import RevokeInvitationUseCase
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
class InvitationRevokedEvent:
    event_id: str
    classroom_id: str
    invitation_code: str
    revoked_by: str
    revoked_at: datetime
    occurred_at: datetime
    expires_at: datetime  # Requis pour projeter le DTO
    event_version: int = 1

# --- DOMAIN AGGREGATE MOCK ---
class DummyClassroom:
    def __init__(self, classroom_id: str):
        self.id = classroom_id
        self._events = []
        self.revoke_invitation_calls = 0

    def revoke_invitation(self, invitation_code: str, requested_by: str, current_time: datetime, event_id: str):
        self.revoke_invitation_calls += 1
        
        if requested_by == "unauthorized_teacher":
            raise UnauthorizedTeacherDomainException("Teacher not authorized.")
        if requested_by == "archived_classroom":
            raise ClassroomArchivedDomainException("Classroom is archived.")
        if invitation_code == "UNKNOWN":
            raise UnknownInvitationDomainException("Invitation not found.")
        if invitation_code == "ALREADY_REVOKED":
            raise AlreadyRevokedDomainException("Invitation already revoked.")

        # Le domaine crée et empile l'événement (CQS)
        event = InvitationRevokedEvent(
            event_id=event_id,
            classroom_id=self.id,
            invitation_code=invitation_code,
            revoked_by=requested_by,
            revoked_at=current_time,
            occurred_at=current_time,
            expires_at=current_time + timedelta(hours=24),
            event_version=1
        )
        self._events.append(event)

    def pull_events(self):
        events = list(self._events)
        self._events.clear()
        return events

# --- FAKE REPOSITORY ---
class FakeClassroomRepository:
    def __init__(self):
        self.classrooms = {}
        self.save_calls = 0

    def find_by_id(self, classroom_id: str):
        return self.classrooms.get(classroom_id)

    def save(self, classroom):
        self.save_calls += 1

# --- FIXTURE ---
@pytest.fixture
def setup_usecase():
    repo = FakeClassroomRepository()
    repo.classrooms["class-123"] = DummyClassroom("class-123")
    
    clock = FakeClock(datetime(2026, 7, 30, 10, 0, 0))
    id_gen = FakeIdGenerator()
    uow = FakeUnitOfWork()
    
    retry_policy = RetryPolicy(
        delay_provider=FakeDelayProvider(),
        retryable_exceptions=(DatabaseLockedException,),
        max_attempts=3,
        initial_delay_ms=0,
        max_delay_ms=0
    )
    
    use_case = RevokeInvitationUseCase(
        repository=repo,
        clock=clock,
        id_generator=id_gen,
        unit_of_work=uow,
        retry_policy=retry_policy
    )
    return use_case, repo, uow

# --- TESTS OBLIGATOIRES ---

def test_revoke_invitation_success(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", invitation_code="SECURE-1")
    
    response = use_case.execute(command)
    
    classroom = repo.classrooms["class-123"]
    assert classroom.revoke_invitation_calls == 1
    assert repo.save_calls == 1
    assert uow.commit_called is True
    
    events_registered = uow.collect_events()
    assert len(events_registered) == 1
    assert isinstance(events_registered[0], InvitationRevokedEvent)
    
    assert isinstance(response, InvitationResponseDTO)
    assert response.status == "REVOKED"
    assert response.invitation_code == "SECURE-1"
    assert response.event_version == 1

def test_revoke_invitation_classroom_not_found(setup_usecase):
    use_case, _, uow = setup_usecase
    command = RevokeInvitationCommand(classroom_id="unknown", teacher_id="teacher-1", invitation_code="SECURE-1")
    
    with pytest.raises(NotFoundApplicationException):
        use_case.execute(command)
    assert uow.commit_called is False

def test_revoke_unknown_invitation(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", invitation_code="UNKNOWN")
    
    with pytest.raises(UnknownInvitationDomainException):
        use_case.execute(command)
        
    assert repo.classrooms["class-123"].revoke_invitation_calls == 1
    assert repo.save_calls == 0
    assert uow.commit_called is False

def test_revoke_already_revoked_invitation(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", invitation_code="ALREADY_REVOKED")
    
    with pytest.raises(AlreadyRevokedDomainException):
        use_case.execute(command)
        
    assert repo.save_calls == 0
    assert uow.commit_called is False

def test_revoke_archived_classroom(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="archived_classroom", invitation_code="SECURE-1")
    
    with pytest.raises(ClassroomArchivedDomainException):
        use_case.execute(command)
        
    assert uow.commit_called is False

def test_revoke_unauthorized_teacher(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="unauthorized_teacher", invitation_code="SECURE-1")
    
    with pytest.raises(UnauthorizedTeacherDomainException):
        use_case.execute(command)
        
    assert uow.commit_called is False

def test_revoke_database_locked_retry(setup_usecase):
    use_case, repo, uow = setup_usecase
    uow.simulate_failure(DatabaseLockedException("SQLite database is locked"))
    
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", invitation_code="SECURE-1")
    
    response = use_case.execute(command)
    
    classroom = repo.classrooms["class-123"]
    # GARANTIE ABSOLUE : La mutation (revoke) n'est appelée qu'UNE SEULE fois, malgré le retry.
    assert classroom.revoke_invitation_calls == 1 
    
    # La sauvegarde (persistance SQLite) a été tentée 2 fois
    assert repo.save_calls == 2
    assert uow.commit_called is True
    assert response.status == "REVOKED"

def test_revoke_retry_exhausted(setup_usecase):
    use_case, repo, uow = setup_usecase
    def always_fail():
        raise DatabaseLockedException("Locked forever")
    uow.commit = always_fail
    
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", invitation_code="SECURE-1")
    
    with pytest.raises(ConcurrencyApplicationException):
        use_case.execute(command)
        
    assert repo.save_calls == 3  # Max attempts de la RetryPolicy

def test_usecase_does_not_access_invitation_entity(setup_usecase):
    use_case, repo, _ = setup_usecase
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", invitation_code="SECURE-1")
    classroom = repo.classrooms["class-123"]
    
    # Le Use Case ne peut pas accéder à l'état interne, on valide qu'il ne tente pas `classroom.invitations`
    assert not hasattr(classroom, "invitations")
    response = use_case.execute(command)
    assert response is not None

def test_usecase_does_not_contain_business_rules(setup_usecase):
    # La commande ne contient aucune information de durée ou de règle.
    # L'exécution repose entièrement sur la validation par l'Agrégat.
    use_case, _, _ = setup_usecase
    command = RevokeInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", invitation_code="SECURE-1")
    response = use_case.execute(command)
    # Si le Use Case contenait une validation locale (if expires_at < now...), le code crasherait ici
    # car l'Entity n'est pas exposée.
    assert response.status == "REVOKED"