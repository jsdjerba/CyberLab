from application.ports.team_repository import TeamRepository
from domain.team.aggregate import Team

class FakeTeamRepository(TeamRepository):
    def __init__(self):
        self.teams: dict[str, Team] = {}
        self.save_calls: int = 0

    def find_by_id(self, team_id: str) -> Team | None:
        return self.teams.get(team_id)

    def save(self, team: Team) -> None:
        self.teams[team.id.value] = team
        self.save_calls += 1