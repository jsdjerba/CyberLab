from application.commands.submit_flag_command import SubmitFlagCommand
from application.dtos.step_result_dto import StepResultDto
from application.ports.lab_repository import LabRepository
from application.ports.lab_instance_repository import LabInstanceRepository
from application.ports.event_bus import EventBus
from application.exceptions.application_errors import LabNotFoundError, LabInstanceNotFoundError

class SubmitFlagUseCase:
    """Squelette initial du Use Case de soumission de flag (Phase 4.7.1)."""

    def __init__(
        self,
        lab_repository: LabRepository,
        lab_instance_repository: LabInstanceRepository,
        event_bus: EventBus
    ):
        self._lab_repository = lab_repository
        self._lab_instance_repository = lab_instance_repository
        self._event_bus = event_bus

    def execute(self, command: SubmitFlagCommand) -> StepResultDto:
        # Squelette de validation / orchestration (Logique métier reportée à la phase suivante)
        instance = self._lab_instance_repository.get_by_id(command.instance_id)
        if not instance:
            raise LabInstanceNotFoundError(command.instance_id)

        lab = self._lab_repository.get_by_id(instance.lab_id)
        if not lab:
            raise LabNotFoundError(str(instance.lab_id))

        # Extraction manuelle et explicite des événements domaine (règle 4)
        if hasattr(instance, "pull_events"):
            events = instance.pull_events()
            if events:
                self._event_bus.publish(events)

        # Retour temporaire d'un DTO neutre pour la validation de structure
        return StepResultDto(
            step_id=str(command.step_id),
            is_valid=False,
            points_awarded=0,
            message="Use Case en cours de construction."
        )