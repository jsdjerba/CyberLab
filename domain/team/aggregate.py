from typing import List, Dict
from datetime import datetime

from domain.team.value_objects.team_id import TeamId
from domain.team.value_objects.classroom_id import ClassroomId
from domain.team.value_objects.student_id import StudentId
from domain.team.value_objects.team_color import TeamColor
from domain.team.value_objects.team_role import TeamRole
from domain.team.value_objects.score import Score
from domain.team.entities.team_member import TeamMember, MemberStatus

from domain.team.events.team_events import (
    TeamDomainEvent, TeamCreatedEvent, StudentAssignedToTeamEvent, 
    RoleAssignedEvent, PointsAwardedEvent, PointsDeductedEvent
)
from domain.team.exceptions.team_exceptions import (
    DuplicateTeamMemberException, TeamCapacityExceededException, 
    CaptainAlreadyExistsException, MemberNotFoundException
)

class Team:
    """Aggregate Root for Team Management"""
    
    def __init__(self, team_id: TeamId, classroom_id: ClassroomId, color: TeamColor, max_size: int):
        self.id = team_id
        self.classroom_id = classroom_id
        self.color = color
        self.max_size = max_size
        self.score = Score(0)
        self.members: Dict[StudentId, TeamMember] = {}
        self._pending_events: List[TeamDomainEvent] = []

    @classmethod
    def create(cls, team_id: TeamId, classroom_id: ClassroomId, color: TeamColor, max_size: int, current_time: datetime, event_id: str) -> 'Team':
        team = cls(team_id, classroom_id, color, max_size)
        team._record_event(TeamCreatedEvent(
            event_id=event_id,
            team_id=team.id.value,
            occurred_at=current_time,
            classroom_id=classroom_id.value,
            color=color.value
        ))
        return team

    def _record_event(self, event: TeamDomainEvent):
        self._pending_events.append(event)

    def pull_events(self) -> List[TeamDomainEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def _has_captain(self) -> bool:
        return any(m.role == TeamRole.CAPTAIN and m.status == MemberStatus.ACTIVE for m in self.members.values())

    def add_member(self, student_id: StudentId, role: TeamRole, current_time: datetime, event_id: str):
        if len(self.members) >= self.max_size:
            raise TeamCapacityExceededException(f"Team has reached its maximum capacity of {self.max_size}.")
        if student_id in self.members:
            raise DuplicateTeamMemberException("Student is already in this team.")
        if role == TeamRole.CAPTAIN and self._has_captain():
            raise CaptainAlreadyExistsException("A team can only have one CAPTAIN.")

        self.members[student_id] = TeamMember(student_id=student_id, role=role, joined_at=current_time)
        
        self._record_event(StudentAssignedToTeamEvent(
            event_id=event_id,
            team_id=self.id.value,
            occurred_at=current_time,
            student_id=student_id.value,
            role=role.value
        ))

    def assign_role(self, student_id: StudentId, new_role: TeamRole, current_time: datetime, event_id: str):
        if student_id not in self.members:
            raise MemberNotFoundException("Student is not part of this team.")
        
        member = self.members[student_id]
        if new_role == TeamRole.CAPTAIN and member.role != TeamRole.CAPTAIN and self._has_captain():
            raise CaptainAlreadyExistsException("A team can only have one CAPTAIN.")

        member.role = new_role
        
        self._record_event(RoleAssignedEvent(
            event_id=event_id,
            team_id=self.id.value,
            occurred_at=current_time,
            student_id=student_id.value,
            role=new_role.value
        ))

    def award_points(self, points: int, reason: str, current_time: datetime, event_id: str):
        self.score = self.score.add(points)
        self._record_event(PointsAwardedEvent(
            event_id=event_id,
            team_id=self.id.value,
            occurred_at=current_time,
            points=points,
            reason=reason
        ))

    def deduct_points(self, points: int, reason: str, current_time: datetime, event_id: str):
        self.score = self.score.subtract(points)
        self._record_event(PointsDeductedEvent(
            event_id=event_id,
            team_id=self.id.value,
            occurred_at=current_time,
            points=points,
            reason=reason
        ))