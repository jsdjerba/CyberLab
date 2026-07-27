from application.use_cases.start_lab_use_case import StartLabUseCase
from application.use_cases.submit_flag_use_case import SubmitFlagUseCase

from infrastructure.repositories.sqlalchemy_lab_repository import SqlAlchemyLabRepository
from infrastructure.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from infrastructure.repositories.sqlalchemy_student_repository import SqlAlchemyStudentRepository

from infrastructure.adapters.event_bus_adapter import EventBusAdapter
from infrastructure.adapters.challenge_validation_adapter import ChallengeValidationAdapter

from domain.labs.services.attempt_policy_service import AttemptPolicyService
from domain.labs.services.scoring_service import ScoringService
from domain.labs.services.flag_validation_service import FlagValidationService

class Container:
    """
    Composition Root / Conteneur d'Injection de Dépendances.
    Assemble les composants sans contenir de logique métier.
    Respecte la Dependency Rule : connait l'App, le Domain et l'Infra.
    """
    def __init__(self, session):
        self._session = session
        self._instances = {}

    # --- Repositories (Scope: Session) ---

    def lab_repository(self) -> SqlAlchemyLabRepository:
        return SqlAlchemyLabRepository(self._session)

    def lab_instance_repository(self) -> SqlAlchemyLabInstanceRepository:
        return SqlAlchemyLabInstanceRepository(self._session)

    def student_repository(self) -> SqlAlchemyStudentRepository:
        return SqlAlchemyStudentRepository(self._session)

    # --- Infrastructure Adapters & Domain Singletons (Scope: Singleton) ---

    def event_bus(self) -> EventBusAdapter:
        if "event_bus" not in self._instances:
            self._instances["event_bus"] = EventBusAdapter()
        return self._instances["event_bus"]

    def flag_validation_service(self) -> FlagValidationService:
        if "flag_validation_service" not in self._instances:
            self._instances["flag_validation_service"] = FlagValidationService()
        return self._instances["flag_validation_service"]

    def challenge_validation_port(self) -> ChallengeValidationAdapter:
        # L'adaptateur de validation a besoin de la session et du service de domaine pur
        return ChallengeValidationAdapter(self._session, self.flag_validation_service())

    def attempt_policy_service(self) -> AttemptPolicyService:
        if "attempt_policy_service" not in self._instances:
            self._instances["attempt_policy_service"] = AttemptPolicyService()
        return self._instances["attempt_policy_service"]

    def scoring_service(self) -> ScoringService:
        if "scoring_service" not in self._instances:
            self._instances["scoring_service"] = ScoringService()
        return self._instances["scoring_service"]

    # --- Application Use Cases (Factory Methods) ---

    def start_lab_use_case(self) -> StartLabUseCase:
        return StartLabUseCase(
            lab_repository=self.lab_repository(),
            lab_instance_repository=self.lab_instance_repository(),
            student_repository=self.student_repository(),
            event_bus=self.event_bus()
            # id_generator utilise sa valeur par défaut (uuid4)
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
            # achievement_service et time_provider utilisent leurs valeurs par défaut
        )