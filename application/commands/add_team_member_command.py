from dataclasses import dataclass
from domain.team.value_objects.team_role import TeamRole

@dataclass(frozen=True)
class AddTeamMemberCommand:
    team_id: str
    student_id: str
    role: TeamRole