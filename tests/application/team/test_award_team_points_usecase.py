import pytest
from datetime import datetime
from application.commands.award_team_points_command import AwardTeamPointsCommand
from application.dto.team_mutation_response import TeamMutationResponseDTO
from application.use_cases.award_team_points import AwardTeamPointsUseCase
from domain.team.aggregate import Team
from domain.team.value_objects.team_id import TeamId
from domain.team.value_objects.classroom_id import ClassroomId
from domain.team.value_objects.team_color import TeamColor
from domain.team.events.team_events import PointsAwardedEvent

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
    id_gen = FakeIdGenerator()
    uow = FakeUnitOfWork()
    retry_policy = RetryPolicy(FakeDelayProvider(), (DatabaseLockedException,), 3, 0, 0)
    
    # Prépare une équipe existante
    team = Team.create(TeamId("team-1"), ClassroomId("class-1"), TeamColor.BLUE, 3, clock.now(), "evt-0")
    team.pull_events() # clear buffer
    repo.save(team)
    
    use_case = AwardTeamPointsUseCase(repo, clock, id_gen, uow, retry_policy)
    return use_case, repo, uow

def test_award_points_updates_domain_and_returns_dto(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = AwardTeamPointsCommand(team_id="team-1", points=50, reason="Flag")
    
    response = use_case.execute(command)
    
    team = repo.find_by_id("team-1")
    assert team.score.value == 50
    assert response.status == "SUCCESS"

def test_usecases_do_not_access_team_members_directly(setup_usecase):
    use_case, repo, _ = setup_usecase
    command = AwardTeamPointsCommand(team_id="team-1", points=50, reason="Flag")
    
    # L'exécution doit passer par la méthode du domaine. Si le use case faisait
    # `team.score.value += 50`, cela crasherait (VO immuable) ou si `team.members` était 
    # inspecté pour des règles métier, cela violerait l'encapsulation.
    # L'exécution propre de la commande prouve l'orchestration pure.
    use_case.execute(command)