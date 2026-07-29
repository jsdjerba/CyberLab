import pytest

from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.correlation_id import CorrelationId

# Ces imports échoueront en TDD
from domain.entities.lab_instance import LabInstance
from domain.policies.attempt_policy import AttemptPolicy
from domain.policies.completion_policy import SingleObjectivePolicy

class FakeFlagValidationService:
    def validate(self, submitted_flag: str, objective_id: ObjectiveId) -> bool:
        return submitted_flag == "CTF{secret}"

def test_submit_flag_is_idempotent_with_same_correlation_id():
    lab = LabInstance(
        student_id=StudentId("stu-1"),
        lab_id=LabId("lab-1"),
        objectives=[ObjectiveId("obj-1")],
        attempt_policy=AttemptPolicy(max_attempts=10, cooldown_seconds=0, lockout_duration_minutes=15),
        completion_policy=SingleObjectivePolicy()
    )
    lab.start(correlation_id=CorrelationId("req-start-1"))
    lab.collect_events() # clear events
    
    validator = FakeFlagValidationService()
    correlation_id = CorrelationId("req-duplicate-submission")
    
    # 1. Premier appel
    result_1 = lab.submit_flag(
        objective_id=ObjectiveId("obj-1"),
        submitted_flag="CTF{wrong}",
        validator=validator,
        correlation_id=correlation_id
    )
    assert len(lab.attempts) == 1
    events_1 = lab.collect_events()
    assert len(events_1) > 0 # FlagSubmitted, FlagRejected
    
    # 2. Deuxième appel (Retry réseau) avec le MÊME CorrelationId
    result_2 = lab.submit_flag(
        objective_id=ObjectiveId("obj-1"),
        submitted_flag="CTF{wrong}",
        validator=validator,
        correlation_id=correlation_id
    )
    
    # Vérifications Idempotence
    assert result_1 == result_2
    assert len(lab.attempts) == 1 # Aucun nouvel attempt créé
    events_2 = lab.collect_events()
    assert len(events_2) == 0 # Aucun événement émis en double
    
    # 3. Troisième appel avec un NOUVEAU CorrelationId
    lab.submit_flag(
        objective_id=ObjectiveId("obj-1"),
        submitted_flag="CTF{wrong}",
        validator=validator,
        correlation_id=CorrelationId("req-new-submission")
    )
    assert len(lab.attempts) == 2 # L'attempt est bien traité