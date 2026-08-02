from dataclasses import dataclass
from domain.team.value_objects.team_color import TeamColor

@dataclass(frozen=True)
class CreateTeamCommand:
    classroom_id: str
    color: TeamColor
    max_size: int