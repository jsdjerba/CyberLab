from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class BadgeDisplayDTO:
    id: str
    name: str

@dataclass(frozen=True)
class GamificationProfileDTO:
    student_id: int
    total_xp: int
    completed_labs: int
    badges: List[BadgeDisplayDTO]

@dataclass(frozen=True)
class LeaderboardEntryDTO:
    username: str
    total_xp: int