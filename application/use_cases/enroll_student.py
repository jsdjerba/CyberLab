"""Use Case d'orchestration pour l'inscription d'un étudiant via code d'invitation."""
from application.commands.enroll_student_command import EnrollStudentCommand
from application.dto.enrollment_response import EnrollmentResponseDTO
from application.exceptions.classroom_application_exceptions import ClassroomNotFoundApplicationException
from application.ports.classroom_repository import ClassroomRepository
from application.ports.unit_of_work import UnitOfWork
from application.ports.clock import Clock
from application.policies.retry_policy import RetryPolicy

from domain.value_objects.classroom_id import ClassroomId
from domain.value_objects.student_id import StudentId
from domain.value_objects.invitation_code import InvitationCode

class EnrollStudentUseCase:
    def __init__(
        self,
        repository: ClassroomRepository,
        unit_of_work: UnitOfWork,
        clock: Clock,
        retry_policy: RetryPolicy,
        id_generator = None # Optionnel si besoin d'IDs additionnels pour les événements d'acceptation
    ):
        self._repository = repository
        self._uow = unit_of_work
        self._clock = clock
        self._retry_policy = retry_policy
        self._id_generator = id_generator

    def execute(self, command: EnrollStudentCommand) -> EnrollmentResponseDTO:
        # 1. Recherche de l'Agrégat Classroom (en dehors de la transaction de commit)
        classroom_id_vo = ClassroomId(command.classroom_id)
        classroom = self._repository.find_by_id(classroom_id_vo)
        
        if classroom is None:
            raise ClassroomNotFoundApplicationException(command.classroom_id)

        # 2. Obtention du temps courant déterministe
        current_time = self._clock.now()

        # 3. Génération des identifiants d'événements si un générateur est présent, sinon fallback déterministe
        accept_event_id = self._id_generator.generate() if self._id_generator else "evt-accept"
        join_event_id = self._id_generator.generate() if self._id_generator else "evt-join"

        # 4. Appel de la méthode métier pure de l'Agrégat (Hors transaction / Hors retry)
        code_vo = InvitationCode(command.invitation_code)
        student_id_vo = StudentId(command.student_id)

        classroom.accept_invitation(
            code=code_vo,
            student_id=student_id_vo,
            current_time=current_time,
            event_accept_id=accept_event_id,
            event_join_id=join_event_id
        )

        # 5. Opération de persistance transactionnelle protégée par le Retry Policy (Concurrence SQLite)
        def persist_action():
            with self._uow:
                self._repository.save(classroom)
                self._uow.commit()

        self._retry_policy.execute(persist_action)

        # 6. Recherche optionnelle de l'équipe de l'étudiant s'il y a lieu, puis retour DTO
        assigned_team = next((t for t in classroom.teams.values() if student_id_vo in t.members), None)
        team_id_str = assigned_team.team_id.value if assigned_team else None

        return EnrollmentResponseDTO(
            classroom_id=command.classroom_id,
            student_id=command.student_id,
            joined_at=current_time,
            team_id=team_id_str
        )