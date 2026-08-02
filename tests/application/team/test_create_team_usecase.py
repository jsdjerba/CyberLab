import pytest
from datetime import datetime
from application.commands.create_team_command import CreateTeamCommand
from application.dto.team_mutation_response import TeamMutationResponseDTO
from application.use_cases.create_team import CreateTeamUseCase
from domain.team.value_objects.team_color import TeamColor
from domain.team.events.team_events import TeamCreatedEvent

from tests.fakes.fake_team_repository import FakeTeamRepository
from tests.fakes.fake_clock import FakeClock
from tests.fakes.fake_id_generator import FakeIdGenerator
from tests.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.fakes.fake_delay_provider import FakeDelayProvider
from application.resilience.retry_policy import RetryPolicy

class DatabaseLockedException(Exception): pass

@pytest.fixture
def setup_usecase():
    repo = FakeTeamRepository()
    clock = FakeClock(datetime(2026, 7, 31, 12, 0, 0))
    id_gen = FakeIdGenerator()  # Generates "id-1", "id-2", etc.
    uow = FakeUnitOfWork()
    retry_policy = RetryPolicy(FakeDelayProvider(), (DatabaseLockedException,), 3, 0, 0)
    
    use_case = CreateTeamUseCase(repo, clock, id_gen, uow, retry_policy)
    return use_case, repo, uow

def test_create_team_generates_id_and_returns_dto(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = CreateTeamCommand(classroom_id="class-1", color=TeamColor.RED, max_size=5)
    
    response = use_case.execute(command)
    
    assert isinstance(response, TeamMutationResponseDTO)
    assert response.team_id == "id-1"  # Correction ici
    assert response.event_id == "id-2" # Correction ici
    assert response.status == "SUCCESS"

def test_create_team_calls_domain_factory(setup_usecase):
    use_case, repo, _ = setup_usecase
    command = CreateTeamCommand(classroom_id="class-1", color=TeamColor.RED, max_size=5)
    use_case.execute(command)
    
    team = repo.find_by_id("id-1") # Correction ici
    assert team is not None
    assert team.classroom_id.value == "class-1"
    assert team.color == TeamColor.RED
    assert team.max_size == 5

def test_create_team_registers_events_and_commits(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = CreateTeamCommand(classroom_id="class-1", color=TeamColor.RED, max_size=5)
    use_case.execute(command)
    
    events = uow.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], TeamCreatedEvent)
    assert repo.save_calls == 1
    assert uow.commit_called is True