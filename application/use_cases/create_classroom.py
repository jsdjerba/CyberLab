"""Use Case d'orchestration pour la création d'une salle de classe."""
from domain.value_objects.tenant_id import TenantId
from domain.value_objects.classroom_id import ClassroomId
from domain.value_objects.classroom_name import ClassroomName
from domain.value_objects.classroom_settings import ClassroomSettings
from domain.value_objects.teacher_id import TeacherId
from domain.entities.classroom import Classroom

from application.commands.create_classroom_command import CreateClassroomCommand
from application.dto.classroom_response import ClassroomResponseDTO
from application.ports.classroom_repository import ClassroomRepository
from application.ports.unit_of_work import UnitOfWork
from application.ports.id_generator import IdGenerator
from application.ports.clock import Clock

class CreateClassroomUseCase:
    def __init__(
        self,
        repository: ClassroomRepository,
        unit_of_work: UnitOfWork,
        id_generator: IdGenerator,
        clock: Clock
    ):
        self._repository = repository
        self._uow = unit_of_work
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, command: CreateClassroomCommand) -> ClassroomResponseDTO:
        # 1. Création des Value Objects (Validation Domain)
        tenant_id = TenantId(command.tenant_id)
        classroom_id = ClassroomId(self._id_generator.generate())
        name = ClassroomName(command.name)
        teacher_id = TeacherId(command.teacher_id)
        settings = ClassroomSettings(
            max_students=command.max_students,
            allow_team_switch=command.allow_team_switch,
            allow_multiple_teachers=command.allow_multiple_teachers
        )

        # 2. Obtenir le temps courant déterministe
        current_time = self._clock.now()

        # 3. Génération des ID nécessaires pour les événements internes de l'agrégat
        event_id_1 = self._id_generator.generate()
        event_id_2 = self._id_generator.generate()

        # 4. Instanciation de l'Agrégat Domain
        classroom = Classroom.create(
            tenant_id=tenant_id,
            classroom_id=classroom_id,
            name=name,
            primary_teacher=teacher_id,
            settings=settings,
            current_time=current_time,
            event_id_1=event_id_1,
            event_id_2=event_id_2
        )

        # 5. Persistance transactionnelle via UoW (avec gestion automatique des erreurs)
        with self._uow:
            self._repository.save(classroom)
            self._uow.commit()

        # 6. Retour du DTO de réponse
        return ClassroomResponseDTO(
            classroom_id=classroom_id.value,
            tenant_id=tenant_id.value,
            name=name.value,
            status=classroom.status.value,
            primary_teacher_id=teacher_id.value
        )