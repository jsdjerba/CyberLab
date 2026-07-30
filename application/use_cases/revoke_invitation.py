from typing import Protocol, Any
from application.commands.revoke_invitation_command import RevokeInvitationCommand
from application.dto.invitation_response import InvitationResponseDTO
from application.exceptions.application_exceptions import NotFoundApplicationException

from application.ports.clock import Clock
from application.ports.id_generator import IdGenerator
from application.ports.unit_of_work import UnitOfWork
from application.resilience.retry_policy import RetryPolicy

class ClassroomRepository(Protocol):
    def find_by_id(self, classroom_id: str) -> Any: ...
    def save(self, classroom: Any) -> None: ...


class RevokeInvitationUseCase:
    """
    Use Case d'orchestration pour la révocation d'une invitation compromise.
    """
    
    def __init__(
        self,
        repository: ClassroomRepository,
        clock: Clock,
        id_generator: IdGenerator,
        unit_of_work: UnitOfWork,
        retry_policy: RetryPolicy
    ):
        self._repository = repository
        self._clock = clock
        self._id_generator = id_generator
        self._uow = unit_of_work
        self._retry_policy = retry_policy

    def execute(self, command: RevokeInvitationCommand) -> InvitationResponseDTO:
        # 1. Chargement (Pas de retry ici)
        classroom = self._repository.find_by_id(command.classroom_id)
        if not classroom:
            raise NotFoundApplicationException(f"Classroom '{command.classroom_id}' not found.")

        # 2. Préparation
        current_time = self._clock.now()
        event_id = self._id_generator.generate()

        # 3. Mutation du Domaine (EXCLUE DU RETRY)
        # La validation d'idempotence (déjà révoquée) ou d'existence se fait dans le Domaine.
        classroom.revoke_invitation(
            invitation_code=command.invitation_code,
            requested_by=command.teacher_id,
            current_time=current_time,
            event_id=event_id
        )

        # 4. Collecte
        events = classroom.pull_events()
        
        invitation_event = next(
            (e for e in events if type(e).__name__ in ("InvitationRevokedEvent", "InvitationRevoked")), 
            None
        )
        
        if not invitation_event:
            raise RuntimeError("Domain Error: Missing InvitationRevokedEvent after mutation.")

        # 5. Persistance Transactionnelle + Outbox
        def persist_state():
            with self._uow:
                self._repository.save(classroom)
                self._uow.register_events(events)
                self._uow.commit()

        # RetryPolicy protège uniquement l'I/O SQLite
        self._retry_policy.execute(persist_state)

        # 6. DTO (CQS)
        return InvitationResponseDTO(
            invitation_code=invitation_event.invitation_code,
            classroom_id=command.classroom_id,
            expires_at=invitation_event.expires_at,
            status="REVOKED",
            event_version=getattr(invitation_event, "event_version", 1)
        )