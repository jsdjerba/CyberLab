from application.queries.get_team_details_query import GetTeamDetailsQuery
from application.dto.team_details_response import TeamDetailsDTO
from application.ports.team_query_repository import TeamQueryRepository
from application.exceptions.team_application_exceptions import TeamNotFoundApplicationException

class GetTeamDetailsUseCase:
    """Orchestrateur de lecture pour les détails d'une équipe. Isolation CQRS totale."""
    def __init__(self, query_repository: TeamQueryRepository):
        self._query_repository = query_repository

    def execute(self, query: GetTeamDetailsQuery) -> TeamDetailsDTO:
        details = self._query_repository.get_team_details(
            team_id=query.team_id, 
            classroom_id=query.classroom_id
        )
        
        if not details:
            raise TeamNotFoundApplicationException(
                f"Team {query.team_id} not found in classroom {query.classroom_id}."
            )
            
        return details