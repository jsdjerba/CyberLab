import uuid
from typing import Callable, Any
from domain.exceptions import LabNotFoundError, StudentNotFoundError
from domain.labs.entities.lab_instance import LabInstance
from application.commands.start_lab_command import StartLabCommand

class StartLabUseCase:
    """
    Cas d'utilisation : Démarrage formel d'un laboratoire par un étudiant.
    Phase B : Orchestration du cycle de vie via l'agrégat LabInstance.
    
    Note architecturale :
    Le repository actuel ne permet pas de rechercher une instance existante par (student_id, lab_id).
    La Phase B crée donc une nouvelle instance sans garantie d'idempotence. 
    Cette capacité sera traitée dans une évolution future du LabInstanceRepositoryPort.
    """

    def __init__(
        self,
        lab_repository: Any,
        lab_instance_repository: Any,
        student_repository: Any,
        event_bus: Any,
        id_generator: Callable[[], str] = lambda: str(uuid.uuid4())
    ):
        self._lab_repository = lab_repository
        self._lab_instance_repository = lab_instance_repository
        self._student_repository = student_repository
        self._event_bus = event_bus
        self._id_generator = id_generator

    def execute(self, command: StartLabCommand) -> str:
        # 1. Vérification de l'existence du Lab
        lab = self._lab_repository.get_by_id(command.lab_id)
        if not lab:
            raise LabNotFoundError(f"Lab {command.lab_id} not found")

        # 2. Vérification de l'existence de l'étudiant via son historique
        student_history = self._student_repository.get_history(command.student_id)
        if student_history is None:
            raise StudentNotFoundError(f"Student {command.student_id} not found")

        # 3. Création de l'instance de laboratoire
        instance_id = self._id_generator()
        instance = LabInstance(
            id=instance_id,
            student_id=command.student_id,
            lab_id=command.lab_id
        )

        # 4. Déclenchement de la transition métier via l'agrégat
        instance.start_lab(lab)

        # 5. Persistance de l'instance
        self._lab_instance_repository.save(instance)

        # 6. Publication des événements de domaine si présents
        events = instance.pull_events()
        if events:
            self._event_bus.publish(events)

        # 7. Retour de l'identifiant de l'instance créée
        return instance_id