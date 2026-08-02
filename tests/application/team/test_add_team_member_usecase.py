import pytest
from datetime import datetime
from application.commands.add_team_member_command import AddTeamMemberCommand
from application.use_cases.add_team_member import AddTeamMemberUseCase
from application.exceptions.team_application_exceptions import TeamNotFoundApplicationException
from domain.team.aggregate import Team
from domain.team.value_objects.team_id import TeamId
from domain.team.value_objects.classroom_id import ClassroomId
from domain.team.value_objects.team_color import TeamColor
from domain.team.value_objects.team_role import TeamRole
from domain.team.exceptions.team_exceptions import DuplicateTeamMemberException

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
    repo.save_calls = 0 # reset counter
    
    use_case = AddTeamMemberUseCase(repo, clock, id_gen, uow, retry_policy)
    return use_case, repo, uow

def test_add_member_success_commits_transaction(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = AddTeamMemberCommand(team_id="team-1", student_id="stu-1", role=TeamRole.ATTACKER)
    
    response = use_case.execute(command)
    assert response.status == "SUCCESS"
    assert repo.save_calls == 1
    assert uow.commit_called is True
    assert len(uow.collect_events()) == 1

def test_add_member_team_not_found(setup_usecase):
    use_case, _, _ = setup_usecase
    command = AddTeamMemberCommand(team_id="unknown", student_id="stu-1", role=TeamRole.ATTACKER)
    with pytest.raises(TeamNotFoundApplicationException):
        use_case.execute(command)

def test_add_member_does_not_retry_domain_exception(setup_usecase):
    use_case, repo, uow = setup_usecase
    command = AddTeamMemberCommand(team_id="team-1", student_id="stu-1", role=TeamRole.ATTACKER)
    use_case.execute(command) # 1er ajout
    
    # 2ème ajout (duplicata)
    with pytest.raises(DuplicateTeamMemberException):
        use_case.execute(command)
        
    # Le Use Case propage l'erreur sans faire de save() additionnel
    assert repo.save_calls == 1 

def test_add_member_database_locked_retries_without_double_mutation(setup_usecase):
    use_case, repo, uow = setup_usecase
    uow.simulate_failure(DatabaseLockedException("DB locked"))
    
    command = AddTeamMemberCommand(team_id="team-1", student_id="stu-1", role=TeamRole.ATTACKER)
    
    response = use_case.execute(command)
    
    assert response.status == "SUCCESS"
    assert repo.save_calls == 2  # A réessayé la sauvegarde
    assert uow.commit_called is True
    # Pas de DuplicateTeamMemberException levée car la mutation Domaine n'a pas été répétée !