from infrastructure.persistence.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.repositories.sqlalchemy_lab_repository import SqlAlchemyLabRepository
from infrastructure.repositories.sqlalchemy_student_repository import SqlAlchemyStudentRepository
from infrastructure.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from infrastructure.bus.in_memory_event_bus import InMemoryEventBus
from application.use_cases.start_lab_use_case import StartLabUseCase
from application.use_cases.submit_flag_use_case import SubmitFlagUseCase
# Importer les Event Handlers futurs ici

class Container:
    """
    Composition Root - Conteneur d'injection de dépendances manuel.
    Gère le cycle de vie de l'EventBus, des repositories et de l'Unit of Work.
    """

    def __init__(self, session):
        self._session = session  # Requis pour test_container_uses_application_session
        self._db_session = session
        
        # Singletons d'infrastructure
        self._event_bus = None
        self._attempt_policy_service = None
        self._challenge_validation_port = None
        self._scoring_service = None
        self._flag_validation_service = None

    def event_bus(self) -> InMemoryEventBus:
        """Retourne l'instance partagée (Singleton) de l'EventBus."""
        if self._event_bus is None:
            self._event_bus = InMemoryEventBus()
            # Enregistrer ici les futurs handlers :
            # self._event_bus.subscribe(LabCompleted, ScoreEngineHandler())
            # self._event_bus.subscribe(LabCompleted, AchievementHandler())
        return self._event_bus

    def unit_of_work_factory(self) -> SqlAlchemyUnitOfWork:
        """Fournit une nouvelle instance d'Unit of Work liée à l'EventBus."""
        return SqlAlchemyUnitOfWork(
            session_factory=self._db_session, 
            event_bus=self.event_bus()
        )

    # --- Repositories ---
    def lab_repository(self):
        return SqlAlchemyLabRepository(self._db_session)

    def student_repository(self):
        return SqlAlchemyStudentRepository(self._db_session)

    def lab_instance_repository(self):
        return SqlAlchemyLabInstanceRepository(self._db_session)

    # --- Services & Adapters factices pour rétrocompatibilité ---
    def attempt_policy_service(self):
        if self._attempt_policy_service is None:
            self._attempt_policy_service = object()
        return self._attempt_policy_service

    def flag_validation_service(self):
        if self._flag_validation_service is None:
            self._flag_validation_service = object()
        return self._flag_validation_service

    def challenge_validation_port(self):
        if self._challenge_validation_port is None:
            # Assurez-vous d'importer ChallengeValidationAdapter si ce port est réel
            from infrastructure.adapters.challenge_validation_adapter import ChallengeValidationAdapter
            self._challenge_validation_port = ChallengeValidationAdapter(
                session=self._db_session,
                flag_validation_service=self.flag_validation_service()
            )
        return self._challenge_validation_port

    def scoring_service(self):
        if self._scoring_service is None:
            self._scoring_service = object()
        return self._scoring_service

    # --- Use Cases ---
    def start_lab_use_case(self) -> StartLabUseCase:
        return StartLabUseCase(
            lab_repository=self.lab_repository(),
            lab_instance_repository=self.lab_instance_repository(),
            student_repository=self.student_repository(),
            event_bus=self.event_bus()
        )

    def submit_flag_use_case(self) -> SubmitFlagUseCase:
        return SubmitFlagUseCase(
            lab_repository=self.lab_repository(),
            lab_instance_repository=self.lab_instance_repository(),
            student_repository=self.student_repository(),
            event_bus=self.event_bus(),
            attempt_policy_service=self.attempt_policy_service(),
            challenge_validation_port=self.challenge_validation_port(),
            scoring_service=self.scoring_service()
        )