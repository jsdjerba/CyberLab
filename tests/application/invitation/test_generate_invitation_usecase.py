import pytest
from datetime import datetime, timedelta
from dataclasses import dataclass

from application.commands.generate_invitation_command import GenerateInvitationCommand
from application.dto.invitation_response import InvitationResponseDTO
from application.use_cases.generate_invitation import GenerateInvitationUseCase
from application.exceptions.application_exceptions import NotFoundApplicationException, ConcurrencyApplicationException
from application.resilience.retry_policy import RetryPolicy

from tests.fakes.fake_clock import FakeClock
from tests.fakes.fake_id_generator import FakeIdGenerator
from tests.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.fakes.fake_delay_provider import FakeDelayProvider

# --- DOMAIN MOCKS (Simulation de l'Agrégat existant) ---

@dataclass(frozen=True)
class InvitationGeneratedEvent:
    event_id: str
    classroom_id: str
    invitation_code: str
    expires_at: datetime
    occurred_at: datetime
    event_version: int = 1

class DomainException(Exception):
    pass

class DummyClassroom:
    def __init__(self, classroom_id: str):
        self.id = classroom_id
        self._events = []
        self.generate_invitation_calls = 0

    def generate_invitation(self, code: str, requested_by: str, validity_hours: int, current_time: datetime, event_id: str):
        self.generate_invitation_calls += 1
        
        # Simulation d'une règle métier (ex: vérification des droits)
        if requested_by == "unauthorized_teacher":
            raise DomainException("Teacher not authorized in this classroom.")
        if requested_by == "archived_classroom":
            raise DomainException("Classroom is archived.")

        # Le domaine calcule la date (Utilisation de timedelta pour éviter les jours hors limites)
        expires_at = current_time + timedelta(hours=validity_hours)
        
        # Le domaine crée et empile l'événement (CQS)
        event = InvitationGeneratedEvent(
            event_id=event_id,
            classroom_id=self.id,
            invitation_code=code,
            expires_at=expires_at,
            occurred_at=current_time,
            event_version=1
        )
        self._events.append(event)

    def pull_events(self):
        events = list(self._events)
        self._events.clear()
        return events

# --- NOUVEAUX FAKES ---

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
        self.counter = 0
    def generate(self) -> str:
        self.counter += 1
        return f"SECURE-{self.counter}"

class DatabaseLockedException(Exception):
    pass

# --- FIXTURES ---

@pytest.fixture
def setup_usecase():
    repo = FakeClassroomRepository()
    repo.classrooms["class-123"] = DummyClassroom("class-123")
    
    code_gen = FakeInvitationCodeGenerator()
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
    
    use_case = GenerateInvitationUseCase(
        repository=repo,
        code_generator=code_gen,
        clock=clock,
        id_generator=id_gen,
        unit_of_work=uow,
        retry_policy=retry_policy
    )
    return use_case, repo, uow

# --- TESTS OBLIGATOIRES ---

def test_generate_invitation_success(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = GenerateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", validity_hours=24)
    
    response = use_case.execute(command)
    
    classroom = repo.classrooms["class-123"]
    assert classroom.generate_invitation_calls == 1
    assert repo.save_calls == 1
    assert uow.commit_called is True
    
    # Vérification du flux Outbox
    events_registered = uow.collect_events()
    assert len(events_registered) == 1
    assert isinstance(events_registered[0], InvitationGeneratedEvent)
    
    # Vérification du DTO (alimenté par l'événement)
    assert isinstance(response, InvitationResponseDTO)
    assert response.invitation_code == "SECURE-1"
    assert response.event_version == 1

def test_generate_invitation_classroom_not_found(setup_usecase):
    use_case, _, uow = setup_usecase
    command = GenerateInvitationCommand(classroom_id="unknown", teacher_id="teacher-1", validity_hours=24)
    
    with pytest.raises(NotFoundApplicationException):
        use_case.execute(command)
    
    assert uow.commit_called is False

def test_generate_invitation_domain_exception_not_retried(setup_usecase):
    use_case, repo, uow = setup_usecase
    # "unauthorized_teacher" force le DummyClassroom à lever une exception métier
    command = GenerateInvitationCommand(classroom_id="class-123", teacher_id="unauthorized_teacher", validity_hours=24)
    
    with pytest.raises(DomainException):
        use_case.execute(command)
        
    classroom = repo.classrooms["class-123"]
    assert classroom.generate_invitation_calls == 1 # Exécuté une seule fois, pas de retry
    assert repo.save_calls == 0
    assert uow.commit_called is False

def test_generate_invitation_database_locked_retry(setup_usecase):
    use_case, repo, uow = setup_usecase
    uow.simulate_failure(DatabaseLockedException("SQLite database is locked"))
    
    command = GenerateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", validity_hours=24)
    
    response = use_case.execute(command)
    
    classroom = repo.classrooms["class-123"]
    # GARANTIE ARCHITECTURALE ABSOLUE : La mutation métier n'est appelée qu'UNE SEULE fois, malgré le retry de la DB.
    assert classroom.generate_invitation_calls == 1 
    
    # La sauvegarde a été tentée deux fois
    assert repo.save_calls == 2
    assert uow.commit_called is True
    assert response.invitation_code == "SECURE-1"

def test_generate_invitation_retry_exhausted(setup_usecase):
    use_case, repo, uow = setup_usecase
    
    # On mock le commit pour qu'il échoue indéfiniment
    def always_fail():
        raise DatabaseLockedException("Locked forever")
    uow.commit = always_fail
    
    command = GenerateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", validity_hours=24)
    
    with pytest.raises(ConcurrencyApplicationException):
        use_case.execute(command)
        
    assert repo.save_calls == 3 # Max attempts (3)

def test_usecase_does_not_access_invitation_collection(setup_usecase):
    use_case, repo, _ = setup_usecase
    command = GenerateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", validity_hours=24)
    
    classroom = repo.classrooms["class-123"]
    # Vérification par l'absurde : le DummyClassroom n'a même pas d'attribut "invitations".
    # Si le Use Case tentait de faire "classroom.invitations", cela crasherait.
    assert not hasattr(classroom, "invitations")
    
    # Le Use Case réussit sans crasher, prouvant qu'il ne lit pas l'état interne.
    response = use_case.execute(command)
    assert response is not None

def test_usecase_does_not_calculate_expiration(setup_usecase):
    use_case, repo, _ = setup_usecase
    command = GenerateInvitationCommand(classroom_id="class-123", teacher_id="teacher-1", validity_hours=48)
    
    response = use_case.execute(command)
    
    # Le Use Case n'a pas fait le calcul. Il a passé "48" au Domaine.
    # On valide que la date retournée est bien celle générée par la logique du Domaine avec timedelta.
    expected_expires_at = datetime(2026, 7, 30, 10, 0, 0) + timedelta(hours=48)
    assert response.expires_at == expected_expires_at