from typing import Callable, Optional, Any
from datetime import datetime

from domain.exceptions import LabInstanceNotFoundError, LabNotFoundError
from application.ports.challenge_validation_port import ChallengeValidationPort

class SubmitFlagUseCase:
    """
    Cas d'utilisation : Soumission d'un flag pour une étape de laboratoire.
    Phase A.5 : Validation des challenges via ChallengeValidationPort.
    """

    def __init__(
        self,
        lab_repository: Any,
        lab_instance_repository: Any,
        student_repository: Any,
        event_bus: Any,
        attempt_policy_service: Any,
        challenge_validation_port: ChallengeValidationPort,
        scoring_service: Any,
        achievement_service: Any = None,
        time_provider: Optional[Callable[[], datetime]] = None,
        **kwargs # Absorbe progress_service s'il est encore injecté par d'anciens tests
    ):
        self._lab_repository = lab_repository
        self._lab_instance_repository = lab_instance_repository
        self._student_repository = student_repository
        self._event_bus = event_bus
        self._attempt_policy_service = attempt_policy_service
        self._challenge_validation_port = challenge_validation_port
        self._scoring_service = scoring_service
        self._achievement_service = achievement_service
        self._time_provider = time_provider or datetime.utcnow

    def execute(self, command: Any) -> bool:
        # 1. Récupération des entités
        instance = self._lab_instance_repository.get_by_id(command.instance_id)
        if not instance:
            raise LabInstanceNotFoundError(f"LabInstance {command.instance_id} not found")

        lab = self._lab_repository.get_by_id(command.lab_id)
        if not lab:
            raise LabNotFoundError(f"Lab {command.lab_id} not found")

        # Mock d'une politique par défaut pour l'exemple
        policy = {} 
        
        # 2. Gestion temporelle
        current_time = self._time_provider()

        # 3. Vérification des politiques de tentative (Guard Clause strict)
        self._attempt_policy_service.can_attempt(
            instance=instance, 
            step_id=command.step_id, 
            policy=policy, 
            current_time=current_time
        )

        # 4. Récupération de l'étape et validation via le Port
        step = lab.get_step(command.step_id)
        
        validation_result = self._challenge_validation_port.validate(
            lab_id=command.lab_id,
            step_id=command.step_id,
            submitted_answer=command.submitted_flag
        )
        
        if not validation_result.success:
            instance.record_attempt(command.step_id, current_time)
            self._lab_instance_repository.save(instance)
            return False

        # 5. Récupération des métriques pour le calcul du score
        attempts_count = instance.get_attempt_count(command.step_id)
        
        # Tech Debt: elapsed_time_seconds is temporarily fixed to 0.
        # Will be replaced by Clock-based timing in Phase C.
        elapsed_time_seconds = 0

        # 6. Calcul du score
        points_awarded = self._scoring_service.calculate_score(
            base_points=step.points,
            attempts_count=attempts_count,
            elapsed_time_seconds=elapsed_time_seconds
        )

        # 7. Mutation de l'état (Progression exclusive via l'agrégat)
        instance.complete_step(command.step_id, lab)
        
        # Mise à jour optionnelle du score si exposée
        if hasattr(instance, "add_score"):
            instance.add_score(points_awarded)

        # 8. Sauvegarde et publication des événements
        self._lab_instance_repository.save(instance)

        return True