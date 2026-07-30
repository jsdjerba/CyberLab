from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class DomainEvent:
    event_id: str
    occurred_at: datetime

@dataclass(frozen=True)
class ClassroomCreated(DomainEvent):
    tenant_id: str
    classroom_id: str
    name: str

@dataclass(frozen=True)
class InstructorAssigned(DomainEvent):
    classroom_id: str
    teacher_id: str
    role: str

@dataclass(frozen=True)
class InvitationGenerated(DomainEvent):
    classroom_id: str
    invitation_code: str
    expires_at: datetime

@dataclass(frozen=True)
class InvitationAccepted(DomainEvent):
    classroom_id: str
    invitation_code: str
    student_id: str

@dataclass(frozen=True)
class InvitationRevoked(DomainEvent):
    classroom_id: str
    invitation_code: str

@dataclass(frozen=True)
class StudentJoinedClassroom(DomainEvent):
    classroom_id: str
    student_id: str

@dataclass(frozen=True)
class StudentRemovedFromClassroom(DomainEvent):
    classroom_id: str
    student_id: str

@dataclass(frozen=True)
class TeamCreated(DomainEvent):
    classroom_id: str
    team_id: str
    name: str

@dataclass(frozen=True)
class StudentAssignedToTeam(DomainEvent):
    classroom_id: str
    student_id: str
    team_id: str

@dataclass(frozen=True)
class StudentRemovedFromTeam(DomainEvent):
    classroom_id: str
    student_id: str
    team_id: str

@dataclass(frozen=True)
class ClassroomArchived(DomainEvent):
    classroom_id: str