from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, kw_only=True)
class TeamDomainEvent:
    event_id: str
    team_id: str
    occurred_at: datetime
    event_version: int = 1

@dataclass(frozen=True, kw_only=True)
class TeamCreatedEvent(TeamDomainEvent):
    classroom_id: str
    color: str

@dataclass(frozen=True, kw_only=True)
class StudentAssignedToTeamEvent(TeamDomainEvent):
    student_id: str
    role: str

@dataclass(frozen=True, kw_only=True)
class RoleAssignedEvent(TeamDomainEvent):
    student_id: str
    role: str

@dataclass(frozen=True, kw_only=True)
class PointsAwardedEvent(TeamDomainEvent):
    points: int
    reason: str

@dataclass(frozen=True, kw_only=True)
class PointsDeductedEvent(TeamDomainEvent):
    points: int
    reason: str