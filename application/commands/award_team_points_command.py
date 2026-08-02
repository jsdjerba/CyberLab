from dataclasses import dataclass

@dataclass(frozen=True)
class AwardTeamPointsCommand:
    team_id: str
    points: int
    reason: str