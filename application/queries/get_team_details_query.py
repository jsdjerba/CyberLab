from dataclasses import dataclass

@dataclass(frozen=True)
class GetTeamDetailsQuery:
    team_id: str
    classroom_id: str
    requested_by: str