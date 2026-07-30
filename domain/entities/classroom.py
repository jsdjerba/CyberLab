"""
Aggregate Root: Classroom
Protège les invariants du domaine, génère des événements déterministes, 
et isole la logique métier de toute préoccupation d'infrastructure.
"""
from typing import List, Dict
from datetime import datetime

# --- Value Objects (Imports stricts et isolés) ---
from domain.value_objects.tenant_id import TenantId
from domain.value_objects.classroom_id import ClassroomId
from domain.value_objects.classroom_name import ClassroomName
from domain.value_objects.classroom_settings import ClassroomSettings
from domain.value_objects.teacher_id import TeacherId
from domain.value_objects.student_id import StudentId
from domain.value_objects.team_id import TeamId
from domain.value_objects.invitation_code import InvitationCode

# --- Enums ---
from domain.enums.classroom_status import ClassroomStatus
from domain.enums.instructor_role import InstructorRole
from domain.enums.team_type import TeamType

# --- Local Entities ---
from domain.entities.classroom_instructor import ClassroomInstructor
from domain.entities.classroom_member import ClassroomMember
from domain.entities.invitation import Invitation
from domain.entities.team import Team

# --- Events & Exceptions ---
from domain.events.classroom_events import *
from domain.exceptions.classroom_exceptions import *


class Classroom:
    def __init__(self, tenant_id: TenantId, classroom_id: ClassroomId, name: ClassroomName, settings: ClassroomSettings):
        self.tenant_id = tenant_id
        self.id = classroom_id
        self.name = name
        self.settings = settings
        self.status = ClassroomStatus.ACTIVE
        self.version: int = 1
        
        self.instructors: Dict[TeacherId, ClassroomInstructor] = {}
        self.members: Dict[StudentId, ClassroomMember] = {}
        self.teams: Dict[TeamId, Team] = {}
        self.invitations: Dict[InvitationCode, Invitation] = {}
        
        self._domain_events: List[DomainEvent] = []

    @classmethod
    def create(cls, tenant_id: TenantId, classroom_id: ClassroomId, name: ClassroomName, primary_teacher: TeacherId, settings: ClassroomSettings, current_time: datetime, event_id_1: str, event_id_2: str) -> 'Classroom':
        classroom = cls(tenant_id, classroom_id, name, settings)
        classroom._record_event(ClassroomCreated(event_id_1, current_time, tenant_id.value, classroom_id.value, name.value))
        classroom.assign_instructor(primary_teacher, InstructorRole.PRIMARY_TEACHER, current_time, event_id_2)
        return classroom

    def _record_event(self, event: DomainEvent):
        self._domain_events.append(event)
        
    def _increment_version(self):
        self.version += 1

    def pull_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def _check_not_archived(self):
        if self.status == ClassroomStatus.ARCHIVED:
            raise ClassroomArchivedException("Opération impossible : la classe est archivée.")

    def archive(self, current_time: datetime, event_id: str):
        self._check_not_archived()
        self.status = ClassroomStatus.ARCHIVED
        self._increment_version()
        self._record_event(ClassroomArchived(event_id, current_time, self.id.value))

    def assign_instructor(self, teacher_id: TeacherId, role: InstructorRole, current_time: datetime, event_id: str):
        self._check_not_archived()
        if teacher_id in self.instructors:
            raise InstructorManagementException("Cet enseignant est déjà assigné à la classe.")
        
        has_primary = any(inst.role == InstructorRole.PRIMARY_TEACHER for inst in self.instructors.values())
        if role == InstructorRole.PRIMARY_TEACHER and has_primary and not self.settings.allow_multiple_teachers:
            raise InstructorManagementException("La classe possède déjà un enseignant principal.")

        self.instructors[teacher_id] = ClassroomInstructor(teacher_id, role, current_time)
        self._increment_version()
        self._record_event(InstructorAssigned(event_id, current_time, self.id.value, teacher_id.value, role.value))

    def generate_invitation(self, code: InvitationCode, expires_at: datetime, current_time: datetime, event_id: str) -> Invitation:
        self._check_not_archived()
        if code in self.invitations:
            raise InvalidInvitationException("Ce code d'invitation existe déjà.")
            
        invitation = Invitation(code, expires_at)
        self.invitations[code] = invitation
        self._increment_version()
        self._record_event(InvitationGenerated(event_id, current_time, self.id.value, code.value, expires_at))
        return invitation
        
    def revoke_invitation(self, code: InvitationCode, current_time: datetime, event_id: str):
        self._check_not_archived()
        invitation = self.invitations.get(code)
        if not invitation:
            raise InvalidInvitationException("Invitation introuvable.")
        
        invitation.revoke()
        self._increment_version()
        self._record_event(InvitationRevoked(event_id, current_time, self.id.value, code.value))

    def accept_invitation(self, code: InvitationCode, student_id: StudentId, current_time: datetime, event_accept_id: str, event_join_id: str):
        self._check_not_archived()
        
        if len(self.members) >= self.settings.max_students:
            raise ClassroomCapacityExceededException(f"Capacité maximale de {self.settings.max_students} atteinte.")
            
        if student_id in self.members:
            raise StudentAlreadyEnrolledException("Étudiant déjà inscrit.")
            
        invitation = self.invitations.get(code)
        if not invitation or not invitation.is_valid(current_time):
            raise InvalidInvitationException("Code invalide, expiré ou révoqué.")

        invitation.accept(student_id, current_time)
        self.members[student_id] = ClassroomMember(student_id, current_time)
        
        self._increment_version()
        self._record_event(InvitationAccepted(event_accept_id, current_time, self.id.value, code.value, student_id.value))
        self._record_event(StudentJoinedClassroom(event_join_id, current_time, self.id.value, student_id.value))
        
    def remove_student(self, student_id: StudentId, current_time: datetime, event_id: str):
        self._check_not_archived()
        if student_id not in self.members:
            raise StudentNotInClassroomException("Étudiant introuvable dans cette classe.")
            
        del self.members[student_id]
        
        # Le retirer également des équipes
        for team in self.teams.values():
            if student_id in team.members:
                team.remove_member(student_id)
                self._record_event(StudentRemovedFromTeam(f"{event_id}-team", current_time, self.id.value, student_id.value, team.team_id.value))
                
        self._increment_version()
        self._record_event(StudentRemovedFromClassroom(event_id, current_time, self.id.value, student_id.value))

    def create_team(self, team_id: TeamId, name: str, team_type: TeamType, current_time: datetime, event_id: str):
        self._check_not_archived()
        if team_id in self.teams:
            raise TeamManagementException("Cette équipe existe déjà.")
            
        self.teams[team_id] = Team(team_id, name, team_type)
        self._increment_version()
        self._record_event(TeamCreated(event_id, current_time, self.id.value, team_id.value, name))

    def assign_student_to_team(self, student_id: StudentId, team_id: TeamId, current_time: datetime, event_id: str):
        self._check_not_archived()
        if student_id not in self.members:
            raise StudentNotInClassroomException("L'étudiant doit être inscrit pour rejoindre une équipe.")
        if team_id not in self.teams:
            raise TeamManagementException("Équipe introuvable.")

        # Vérifier si l'étudiant est déjà dans une équipe
        current_team = next((t for t in self.teams.values() if student_id in t.members), None)
        
        if current_team:
            if current_team.team_id == team_id:
                return # Déjà dans cette équipe
            if not self.settings.allow_team_switch:
                raise TeamManagementException("Le changement d'équipe n'est pas autorisé par les paramètres de la classe.")
            
            current_team.remove_member(student_id)
            self._record_event(StudentRemovedFromTeam(f"{event_id}-leave", current_time, self.id.value, student_id.value, current_team.team_id.value))

        self.teams[team_id].add_member(student_id)
        self._increment_version()
        self._record_event(StudentAssignedToTeam(event_id, current_time, self.id.value, student_id.value, team_id.value))