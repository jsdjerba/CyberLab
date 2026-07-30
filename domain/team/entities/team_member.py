from dataclasses import dataclass
from datetime import datetime
from domain.team.value_objects.student_id import StudentId
from domain.team.value_objects.team_role import TeamRole
from enum import Enum

class MemberStatus(Enum):
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"

@dataclass
class TeamMember:
    student_id: StudentId
    role: TeamRole
    joined_at: datetime
    status: MemberStatus = MemberStatus.ACTIVE