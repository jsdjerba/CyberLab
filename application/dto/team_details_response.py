from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass(frozen=True)
class TeamMemberDTO:
    student_id: str
    role: str
    joined_at: datetime

@dataclass(frozen=True)
class TeamDetailsDTO:
    team_id: str
    classroom_id: str
    color: str
    score: int
    members: List[TeamMemberDTO]