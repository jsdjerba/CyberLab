from typing import Protocol, Any
from application.commands.rotate_invitation_command import RotateInvitationCommand
from application.dto.invitation_response import InvitationResponseDTO
from application.exceptions.application_exceptions import NotFoundApplicationException

from application.ports.clock import Clock
from application.ports.id_generator import IdGenerator
from application.ports.unit_of_work import UnitOfWork
from application.resilience.retry_policy import RetryPolicy

class InvitationCodeGenerator(Protocol):
    def generate(self) -> str: ...

class ClassroomRepository(Protocol):
    def find_by_id(self, classroom_id: str) -> Any: ...
    def save(self, classroom: Any) -> None: ...


class RotateInvitationUseCase:
    """
    Use Case d'orchestration pour la rotation d'une invitation compromise.
    """
    
    def __init__(
        self,
        repository: ClassroomRepository,
        code_generator: InvitationCodeGenerator,
        clock: Clock,
        id_generator: IdGenerator,
        unit_of_work: UnitOfWork,
        retry_policy: RetryPolicy
    ):
        self._repository = repository
        self._code_generator = code_generator
        self._clock = clock
        self._id_generator = id_generator
        self._uow = unit_of_work
        self._retry_policy = retry_policy

    def execute(self, command: RotateInvitationCommand) -> InvitationResponseDTO:
        # 1. Chargement
        classroom = self._repository.find_by_id(command.classroom_id)
        if not classroom:
            raise NotFoundApplicationException(f"Classroom '{command.classroom_id}' not found.")

        # 2. Préparation
        current_time = self._clock.now()
        event_id = self._id_generator.generate()
        
        # 3. Génération du nouveau code via le Port Applicatif
        new_code = self._code_generator.generate()

        # 4. Mutation Domaine (HORS RETRY POLICY)
        classroom.rotate_invitation(
            old_invitation_code=command.old_invitation_code,
            new_invitation_code=new_code,
            requested_by=command.teacher_id,
            current_time=current_time,
            validity_hours=command.validity_hours,
            event_id=event_id
        )

        # 5. Extraction Event (Snapshot)
        events = classroom.pull_events()
        
        rotated_event = next(
            (e for e in events if type(e).__name__ in ("InvitationRotatedEvent", "InvitationRotated")), 
            None
        )
        
        if not rotated_event:
            raise RuntimeError("Domain Error: Missing InvitationRotatedEvent after mutation.")

        # 6. Persistance Transactionnelle + Outbox
        def persist_state():
            with self._uow:
                self._repository.save(classroom)
                self._uow.register_events(events)
                self._uow.commit()

        # RetryPolicy protège UNIQUEMENT les I/O
        self._retry_policy.execute(persist_state)

        # 7. Projection CQS depuis l'Événement
        return InvitationResponseDTO(
            invitation_code=rotated_event.new_invitation_code,
            classroom_id=command.classroom_id,
            expires_at=rotated_event.new_expires_at,
            status="ACTIVE",
            event_version=getattr(rotated_event, "event_version", 1)
        )