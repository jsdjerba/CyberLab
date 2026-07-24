from datetime import datetime, timedelta
import pytest
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.policies.submission_policy import SubmissionPolicy
from domain.labs.services.attempt_policy_service import AttemptPolicyService
from domain.labs.exceptions import MaxAttemptsReached, CooldownActive, InvalidSubmissionPolicy

@pytest.fixture
def attempt_service():
    return AttemptPolicyService()

@pytest.fixture
def base_time():
    return datetime(2026, 7, 22, 12, 0, 0)

def test_unlimited_attempts_with_none(attempt_service, base_time):
    # A. SubmissionPolicy(max_attempts=None) => toutes les tentatives autorisées
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    policy = SubmissionPolicy(max_attempts=None, cooldown_seconds=0)
    step_id = StepId("s1")

    for _ in range(50):
        instance.record_attempt(step_id, base_time)

    assert attempt_service.can_attempt(instance, step_id, policy, base_time) is True

def test_zero_attempts_allowed(attempt_service, base_time):
    # B. SubmissionPolicy(max_attempts=0) => aucune tentative autorisée
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    policy = SubmissionPolicy(max_attempts=0, cooldown_seconds=0)
    step_id = StepId("s1")

    with pytest.raises(MaxAttemptsReached) as exc_info:
        attempt_service.can_attempt(instance, step_id, policy, base_time)
    assert exc_info.value.max_attempts == 0

def test_refused_by_cooldown_does_not_mutate(attempt_service, base_time):
    # C. Tentative refusée par cooldown => record_attempt non appelé
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    policy = SubmissionPolicy(max_attempts=5, cooldown_seconds=60)
    step_id = StepId("s1")

    instance.record_attempt(step_id, base_time - timedelta(seconds=10))
    initial_count = instance.get_attempt_count(step_id)

    with pytest.raises(CooldownActive):
        attempt_service.can_attempt(instance, step_id, policy, base_time)

    # Vérification que l'état n'a pas changé
    assert instance.get_attempt_count(step_id) == initial_count

def test_independent_steps_history(attempt_service, base_time):
    # D. Deux étapes différentes => historique indépendant
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    policy = SubmissionPolicy(max_attempts=1, cooldown_seconds=60)
    step_a = StepId("step_a")
    step_b = StepId("step_b")

    instance.record_attempt(step_a, base_time)

    with pytest.raises(MaxAttemptsReached):
        attempt_service.can_attempt(instance, step_a, policy, base_time)

    assert attempt_service.can_attempt(instance, step_b, policy, base_time) is True

def test_legacy_attempts_property_compatibility(base_time):
    # E. Ancienne API LabInstance.attempts toujours fonctionnelle
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    step_id = StepId("s1")
    instance.record_attempt(step_id, base_time)

    legacy_dict = instance.attempts
    assert isinstance(legacy_dict, dict)
    assert legacy_dict.get("s1") == 1

def test_cooldown_fractional_remaining_rounding(attempt_service, base_time):
    # F. Cooldown avec 0.5 seconde restante => remaining_seconds == 1
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    policy = SubmissionPolicy(max_attempts=5, cooldown_seconds=10)
    step_id = StepId("s1")

    # Il s'est écoulé 9.2 secondes, reste 0.8 s
    instance.record_attempt(step_id, base_time - timedelta(seconds=9.2))

    with pytest.raises(CooldownActive) as exc_info:
        attempt_service.can_attempt(instance, step_id, policy, base_time)
    
    assert exc_info.value.remaining_seconds == 1

def test_invalid_policy_parameters():
    with pytest.raises(InvalidSubmissionPolicy):
        SubmissionPolicy(max_attempts=-2, cooldown_seconds=10)

    with pytest.raises(InvalidSubmissionPolicy):
        SubmissionPolicy(max_attempts=3, cooldown_seconds=-1)