from typing import Protocol, Any
from application.commands.generate_invitation_command import GenerateInvitationCommand
from application.dto.invitation_response import InvitationResponseDTO
from application.exceptions.application_exceptions import NotFoundApplicationException

from application.ports.clock import Clock
from application.ports.id_generator import IdGenerator
from application.ports.unit_of_work import UnitOfWork
from application.resilience.retry_policy import RetryPolicy

# Contrats locaux des ports nécessaires pour ce flux
class InvitationCodeGenerator(Protocol):
    def generate(self) -> str:
        ...

class ClassroomRepository(Protocol):
    def find_by_id(self, classroom_id: str) -> Any:
        ...
    def save(self, classroom: Any) -> None:
        ...


class GenerateInvitationUseCase:
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

    def execute(self, command: GenerateInvitationCommand) -> InvitationResponseDTO:
        # 1. Chargement (Pas de retry ici, lecture simple)
        classroom = self._repository.find_by_id(command.classroom_id)
        if not classroom:
            raise NotFoundApplicationException(f"Classroom '{command.classroom_id}' not found.")

        # 2. Préparation des dépendances
        current_time = self._clock.now()
        raw_code = self._code_generator.generate()
        event_id = self._id_generator.generate()

        # 3. Mutation du Domaine (EXCLUE DE LA RETRY POLICY)
        classroom.generate_invitation(
            code=raw_code,
            requested_by=command.teacher_id,
            validity_hours=command.validity_hours,
            current_time=current_time,
            event_id=event_id
        )

        # 4. Collecte des événements (Snapshot de la mutation)
        events = classroom.pull_events()
        
        invitation_event = next(
            (e for e in events if type(e).__name__ in ("InvitationGeneratedEvent", "InvitationGenerated")), 
            None
        )
        
        if not invitation_event:
            raise RuntimeError("Domain Error: Missing InvitationGeneratedEvent after mutation.")

        # 5. Persistance Transactionnelle et Outbox
        def persist_state():
            with self._uow:
                self._repository.save(classroom)
                self._uow.register_events(events)
                self._uow.commit()

        # Seule la sauvegarde est réessayée en cas de DatabaseLocked
        self._retry_policy.execute(persist_state)

        # 6. Projection du DTO depuis l'Événement (Respect du CQRS)
        return InvitationResponseDTO(
            invitation_code=invitation_event.invitation_code,
            classroom_id=command.classroom_id,
            expires_at=invitation_event.expires_at,
            status="ACTIVE",
            event_version=getattr(invitation_event, "event_version", 1)
        )