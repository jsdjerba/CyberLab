from typing import Optional, List
from datetime import datetime

# IMPORTS ANTICIPÉS (Provoqueront des ModuleNotFoundError en phase RED)
from application.dto.leaderboard_response import LeaderboardResponseDTO, LeaderboardItemDTO
from application.dto.team_details_response import TeamDetailsDTO, TeamMemberDTO

class FakeTeamQueryRepository:
    """
    Simule le port de lecture CQRS. Ne manipule AUCUN Aggregate Root.
    Retourne directement des DTOs plats.
    """
    def __init__(self):
        self.leaderboards: dict[str, LeaderboardResponseDTO] = {}
        self.team_details: dict[str, TeamDetailsDTO] = {}

    def get_leaderboard(self, classroom_id: str) -> LeaderboardResponseDTO:
        # Retourne le DTO pré-rempli ou un DTO vide
        return self.leaderboards.get(
            classroom_id, 
            LeaderboardResponseDTO(classroom_id=classroom_id, leaderboard=[])
        )

    def get_team_details(self, team_id: str, classroom_id: str) -> Optional[TeamDetailsDTO]:
        # Vérifie l'appartenance à la classe (Anti-IDOR simulé)
        details = self.team_details.get(team_id)
        if details and details.classroom_id == classroom_id:
            return details
        return None