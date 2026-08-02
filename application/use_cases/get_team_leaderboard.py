from application.queries.get_team_leaderboard_query import GetTeamLeaderboardQuery
from application.dto.leaderboard_response import LeaderboardResponseDTO
from application.ports.team_query_repository import TeamQueryRepository

class GetTeamLeaderboardUseCase:
    """Orchestrateur de lecture pour le classement des équipes. Isolation CQRS totale."""
    def __init__(self, query_repository: TeamQueryRepository):
        self._query_repository = query_repository

    def execute(self, query: GetTeamLeaderboardQuery) -> LeaderboardResponseDTO:
        if not query.classroom_id:
            raise ValueError("classroom_id is required to fetch leaderboard")
            
        return self._query_repository.get_leaderboard(classroom_id=query.classroom_id)