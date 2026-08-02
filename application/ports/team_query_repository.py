from typing import Protocol, Optional
from application.dto.leaderboard_response import LeaderboardResponseDTO
from application.dto.team_details_response import TeamDetailsDTO

class TeamQueryRepository(Protocol):
    def get_leaderboard(self, classroom_id: str) -> LeaderboardResponseDTO:
        ...

    def get_team_details(self, team_id: str, classroom_id: str) -> Optional[TeamDetailsDTO]:
        ...