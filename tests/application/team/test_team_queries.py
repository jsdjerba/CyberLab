import pytest
import inspect
from datetime import datetime

# IMPORTS ANTICIPÉS (API Idéale souhaitée)
from application.queries.get_team_leaderboard_query import GetTeamLeaderboardQuery
from application.queries.get_team_details_query import GetTeamDetailsQuery
from application.use_cases.get_team_leaderboard import GetTeamLeaderboardUseCase
from application.use_cases.get_team_details import GetTeamDetailsUseCase
from application.dto.leaderboard_response import LeaderboardResponseDTO, LeaderboardItemDTO
from application.dto.team_details_response import TeamDetailsDTO, TeamMemberDTO
from application.exceptions.team_application_exceptions import TeamNotFoundApplicationException

from tests.fakes.fake_team_query_repository import FakeTeamQueryRepository

@pytest.fixture
def query_repo():
    return FakeTeamQueryRepository()

@pytest.fixture
def leaderboard_use_case(query_repo):
    return GetTeamLeaderboardUseCase(query_repository=query_repo)

@pytest.fixture
def details_use_case(query_repo):
    return GetTeamDetailsUseCase(query_repository=query_repo)

# --- TESTS : LEADERBOARD ---

def test_get_leaderboard_returns_sorted_dto(query_repo, leaderboard_use_case):
    # Setup du Fake avec des DTOs purs (pas d'Agrégat)
    query_repo.leaderboards["class-1"] = LeaderboardResponseDTO(
        classroom_id="class-1",
        leaderboard=[
            LeaderboardItemDTO(team_id="team-1", color="RED", score=150, rank=1, members_count=3),
            LeaderboardItemDTO(team_id="team-2", color="BLUE", score=100, rank=2, members_count=2)
        ]
    )
    
    query = GetTeamLeaderboardQuery(classroom_id="class-1", requested_by="teacher-1")
    response = leaderboard_use_case.execute(query)
    
    assert isinstance(response, LeaderboardResponseDTO)
    assert len(response.leaderboard) == 2
    assert response.leaderboard[0].score == 150
    assert response.leaderboard[0].rank == 1
    assert response.leaderboard[1].score == 100

def test_get_leaderboard_empty(query_repo, leaderboard_use_case):
    query = GetTeamLeaderboardQuery(classroom_id="class-empty", requested_by="teacher-1")
    response = leaderboard_use_case.execute(query)
    
    assert isinstance(response, LeaderboardResponseDTO)
    assert response.classroom_id == "class-empty"
    assert len(response.leaderboard) == 0  # Ne doit pas planter, juste retourner une liste vide

# --- TESTS : TEAM DETAILS ---

def test_get_team_details_success(query_repo, details_use_case):
    # Setup du Fake
    query_repo.team_details["team-1"] = TeamDetailsDTO(
        team_id="team-1",
        classroom_id="class-1",
        color="RED",
        score=150,
        members=[
            TeamMemberDTO(student_id="stu-1", role="CAPTAIN", joined_at=datetime(2026, 8, 1)),
            TeamMemberDTO(student_id="stu-2", role="ATTACKER", joined_at=datetime(2026, 8, 2))
        ]
    )
    
    query = GetTeamDetailsQuery(team_id="team-1", classroom_id="class-1", requested_by="teacher-1")
    response = details_use_case.execute(query)
    
    assert response.team_id == "team-1"
    assert response.score == 150
    assert len(response.members) == 2
    assert response.members[0].role == "CAPTAIN"

def test_get_team_details_not_found(query_repo, details_use_case):
    query = GetTeamDetailsQuery(team_id="team-unknown", classroom_id="class-1", requested_by="teacher-1")
    
    with pytest.raises(TeamNotFoundApplicationException):
        details_use_case.execute(query)

def test_get_team_details_cross_classroom_prevented(query_repo, details_use_case):
    # Setup équipe dans class-1
    query_repo.team_details["team-1"] = TeamDetailsDTO("team-1", "class-1", "RED", 150, [])
    
    # Tentative d'accès depuis class-2 (IDOR)
    query = GetTeamDetailsQuery(team_id="team-1", classroom_id="class-2", requested_by="teacher-2")
    
    with pytest.raises(TeamNotFoundApplicationException):
        details_use_case.execute(query)

# --- TESTS : ARCHITECTURE CQRS (GUARDS) ---

def test_architecture_isolation_cqrs_leaderboard():
    init_signature = inspect.signature(GetTeamLeaderboardUseCase.__init__)
    params = init_signature.parameters
    
    # Interdictions formelles
    assert "unit_of_work" not in params, "Le Read Side ne doit jamais manipuler l'Outbox ou les transactions"
    assert "retry_policy" not in params, "Le Read Side n'a pas besoin de RetryPolicy"
    assert "repository" not in params, "Le Read Side ne doit pas utiliser le Repository d'écriture"
    
    # Port requis
    assert "query_repository" in params

def test_architecture_no_aggregate_loaded():
    # Vérifie statiquement que l'Aggregate Root n'est pas importé dans les Use Cases CQRS
    try:
        import application.use_cases.get_team_leaderboard as leaderboard_module
        assert "Team" not in leaderboard_module.__dict__, "Team Aggregate détecté dans le Use Case de lecture !"
        assert "TeamMember" not in leaderboard_module.__dict__, "TeamMember Entity détectée !"
    except ModuleNotFoundError:
        pass # Normal en phase RED