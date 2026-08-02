from dataclasses import dataclass

@dataclass(frozen=True)
class GetTeamLeaderboardQuery:
    classroom_id: str
    requested_by: str