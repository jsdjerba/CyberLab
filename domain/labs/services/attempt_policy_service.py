import math
from datetime import datetime
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.step_id import StepId
from domain.labs.policies.submission_policy import SubmissionPolicy
from domain.labs.exceptions import MaxAttemptsReached, CooldownActive, InvalidSubmissionPolicy

class AttemptPolicyService:
    """Domain Service responsable de l'évaluation des politiques de soumission.
    
    Contrat métier :
    - can_attempt() : vérifie uniquement l'autorisation et ne modifie jamais l'état.
    - record_attempt() : demeure la responsabilité du Use Case ou de LabInstance après exécution.
    
    Scénarios gérés :
    1. Cooldown actif => lève CooldownActive, aucune tentative enregistrée.
    2. Tentative autorisée (mauvais flag) => l'appelant déclenche record_attempt().
    3. Tentative autorisée (bon flag) => géré par le flux de complétion (SubmitFlagUseCase).
    """

    def can_attempt(
        self,
        instance: LabInstance,
        step_id: StepId,
        policy: SubmissionPolicy,
        current_time: datetime
    ) -> bool:
        if policy.cooldown_seconds < 0 or (policy.max_attempts is not None and policy.max_attempts < 0):
            raise InvalidSubmissionPolicy()

        attempts = instance.get_attempt_count(step_id)

        # 1. Vérification du quota maximum d'essais
        if policy.max_attempts is not None:
            if attempts >= policy.max_attempts:
                raise MaxAttemptsReached(step_id=step_id, attempts_count=attempts, max_attempts=policy.max_attempts)

        # 2. Vérification du cooldown avec calcul précis par arrondi supérieur (math.ceil)
        last_time = instance.get_last_attempt_time(step_id)
        if last_time is not None and policy.cooldown_seconds > 0:
            elapsed = (current_time - last_time).total_seconds()
            if elapsed < policy.cooldown_seconds:
                remaining = math.ceil(policy.cooldown_seconds - elapsed)
                raise CooldownActive(step_id=step_id, remaining_seconds=max(1, remaining))

        return True