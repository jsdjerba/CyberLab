from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class LeaderboardItemDTO:
    team_id: str
    color: str
    score: int
    rank: int
    members_count: int

@dataclass(frozen=True)
class LeaderboardResponseDTO:
    classroom_id: str
    leaderboard: List[LeaderboardItemDTO]