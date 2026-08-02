from dataclasses import dataclass

@dataclass(frozen=True)
class TeamMutationResponseDTO:
    team_id: str
    event_id: str
    status: str