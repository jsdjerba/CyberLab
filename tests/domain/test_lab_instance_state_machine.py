import pytest

from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.correlation_id import CorrelationId
from domain.value_objects.lab_status import LabStatus

# Ces imports échoueront en TDD
from domain.entities.lab_instance import LabInstance
from domain.policies.attempt_policy import AttemptPolicy
from domain.policies.completion_policy import AllObjectivesPolicy
from domain.events.lab_started import LabStarted
from domain.events.flag_submitted import FlagSubmitted
from domain.events.flag_rejected import FlagRejected
from domain.events.flag_validated import FlagValidated
from domain.events.objective_completed import ObjectiveCompleted
from domain.events.lab_completed import LabCompleted
from domain.events.lab_locked_out import LabLockedOut
from domain.exceptions import LabNotStartedException, LabAlreadyCompletedException, LabLockedOutException

class FakeFlagValidationService:
    def __init__(self, expected_flag: str):
        self.expected_flag = expected_flag
    def validate(self, submitted_flag: str, objective_id: ObjectiveId) -> bool:
        return submitted_flag == self.expected_flag

@pytest.fixture
def base_lab():
    return LabInstance(
        student_id=StudentId("stu-1"),
        lab_id=LabId("lab-101"),
        objectives=[ObjectiveId("obj-1"), ObjectiveId("obj-2")],
        attempt_policy=AttemptPolicy(max_attempts=3, cooldown_seconds=0, lockout_duration_minutes=15),
        completion_policy=AllObjectivesPolicy()
    )

def test_lab_instance_initial_state(base_lab):
    assert base_lab.status == LabStatus.NOT_STARTED
    assert len(base_lab.attempts) == 0
    assert len(base_lab.collect_events()) == 0

def test_start_from_not_started(base_lab):
    correlation_id = CorrelationId("req-start-1")
    base_lab.start(correlation_id=correlation_id)
    
    assert base_lab.status == LabStatus.IN_PROGRESS
    events = base_lab.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], LabStarted)
    assert events[0].correlation_id == correlation_id

def test_start_is_idempotent(base_lab):
    correlation_id_1 = CorrelationId("req-start-1")
    correlation_id_2 = CorrelationId("req-start-2")
    
    # Premier appel
    base_lab.start(correlation_id=correlation_id_1)
    events_1 = base_lab.collect_events()
    
    # Deuxième appel (ex: double clic étudiant)
    base_lab.start(correlation_id=correlation_id_2)
    events_2 = base_lab.collect_events()
    
    assert base_lab.status == LabStatus.IN_PROGRESS
    assert len(events_1) == 1
    # Aucun nouvel événement ne doit être émis si le lab était déjà démarré
    assert len(events_2) == 0 

def test_submit_flag_requires_in_progress_state(base_lab):
    validator = FakeFlagValidationService("CTF{secret}")
    
    with pytest.raises(LabNotStartedException, match="Le laboratoire n'est pas démarré"):
        base_lab.submit_flag(
            objective_id=ObjectiveId("obj-1"),
            submitted_flag="CTF{secret}",
            validator=validator,
            correlation_id=CorrelationId("req-sub-1")
        )

def test_submit_wrong_flag_creates_attempt_and_event(base_lab):
    base_lab.start(correlation_id=CorrelationId("req-start-1"))
    base_lab.collect_events() # clear
    
    validator = FakeFlagValidationService("CTF{secret}")
    base_lab.submit_flag(
        objective_id=ObjectiveId("obj-1"),
        submitted_flag="CTF{wrong}",
        validator=validator,
        correlation_id=CorrelationId("req-sub-1")
    )
    
    assert base_lab.status == LabStatus.IN_PROGRESS
    assert len(base_lab.attempts) == 1
    
    attempt = base_lab.attempts[0]
    # SÉCURITÉ OBLIGATOIRE : Aucune donnée sensible dans l'historique
    assert not hasattr(attempt, 'plaintext_flag')
    assert not hasattr(attempt, 'submitted_flag')
    assert not hasattr(attempt, 'flag')
    assert attempt.is_correct is False
    
    events = base_lab.collect_events()
    assert any(isinstance(e, FlagSubmitted) for e in events)
    assert any(isinstance(e, FlagRejected) for e in events)

def test_submit_correct_objective_completes_objective(base_lab):
    base_lab.start(correlation_id=CorrelationId("req-start-1"))
    base_lab.collect_events() # clear
    
    validator = FakeFlagValidationService("CTF{secret}")
    base_lab.submit_flag(
        objective_id=ObjectiveId("obj-1"),
        submitted_flag="CTF{secret}",
        validator=validator,
        correlation_id=CorrelationId("req-sub-1")
    )
    
    events = base_lab.collect_events()
    assert any(isinstance(e, FlagValidated) for e in events)
    assert any(isinstance(e, ObjectiveCompleted) for e in events)

def test_lab_completion_requires_completion_policy(base_lab):
    base_lab.start(correlation_id=CorrelationId("req-start-1"))
    validator = FakeFlagValidationService("CTF{secret}")
    
    # Le lab exige 2 objectifs (AllObjectivesPolicy)
    base_lab.submit_flag(ObjectiveId("obj-1"), "CTF{secret}", validator, CorrelationId("req-sub-1"))
    assert base_lab.status == LabStatus.IN_PROGRESS
    
    base_lab.submit_flag(ObjectiveId("obj-2"), "CTF{secret}", validator, CorrelationId("req-sub-2"))
    assert base_lab.status == LabStatus.COMPLETED
    
    events = base_lab.collect_events()
    assert any(isinstance(e, LabCompleted) for e in events)

def test_locked_lab_rejects_submission(base_lab):
    base_lab.start(correlation_id=CorrelationId("req-start-1"))
    validator = FakeFlagValidationService("CTF{secret}")
    
    # 3 échecs (max_attempts = 3)
    base_lab.submit_flag(ObjectiveId("obj-1"), "CTF{w1}", validator, CorrelationId("r-1"))
    base_lab.submit_flag(ObjectiveId("obj-1"), "CTF{w2}", validator, CorrelationId("r-2"))
    base_lab.submit_flag(ObjectiveId("obj-1"), "CTF{w3}", validator, CorrelationId("r-3"))
    
    assert base_lab.status == LabStatus.LOCKED_OUT
    events = base_lab.collect_events()
    assert any(isinstance(e, LabLockedOut) for e in events)
    
    # La 4ème tentative doit lever l'exception
    with pytest.raises(LabLockedOutException):
         base_lab.submit_flag(ObjectiveId("obj-1"), "CTF{w4}", validator, CorrelationId("r-4"))

def test_completed_lab_is_immutable(base_lab):
    base_lab.start(correlation_id=CorrelationId("req-start-1"))
    validator = FakeFlagValidationService("CTF{secret}")
    
    base_lab.submit_flag(ObjectiveId("obj-1"), "CTF{secret}", validator, CorrelationId("req-sub-1"))
    base_lab.submit_flag(ObjectiveId("obj-2"), "CTF{secret}", validator, CorrelationId("req-sub-2"))
    assert base_lab.status == LabStatus.COMPLETED
    
    with pytest.raises(LabAlreadyCompletedException, match="Le laboratoire est déjà complété"):
        base_lab.submit_flag(ObjectiveId("obj-1"), "CTF{secret}", validator, CorrelationId("req-sub-3"))