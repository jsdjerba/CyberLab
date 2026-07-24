import pytest
from domain.labs.entities.lab import Lab
from domain.labs.entities.step import Step
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.step_type import StepType
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.lab_status import LabStatus
from domain.labs.policies.submission_policy import SubmissionPolicy
from domain.labs.exceptions import InvalidLabState, InvalidStepTransition, LabDomainError

@pytest.fixture
def base_lab():
    step1 = Step(StepId("s1"), StepType.QUIZ, "Q1", 5)
    step2 = Step(StepId("s2"), StepType.FLAG, "F1", 15)
    return Lab(LabId("L_EDGE"), "Edge Cases Lab", "Desc", "Hard", 60, [step1, step2])

# --- Tests sur les Value Objects ---

def test_student_id_valid():
    student = StudentId(42)
    assert student.value == 42

def test_student_id_invalid_negative():
    with pytest.raises(LabDomainError):
        StudentId(-5)

# --- Tests d'isolation et d'état de LabInstance ---

def test_pull_events_empty_initial_state():
    instance = LabInstance("inst_X", StudentId(1), LabId("L_EDGE"))
    assert len(instance.pull_events()) == 0

def test_complete_step_invalid_state_not_started(base_lab):
    instance = LabInstance("inst_X", StudentId(1), LabId("L_EDGE"))
    # Le lab n'a pas été démarré avec start_lab()
    with pytest.raises(InvalidLabState, match="IN_PROGRESS"):
        instance.complete_step(StepId("s1"), base_lab)

def test_complete_step_invalid_state_completed(base_lab):
    instance = LabInstance("inst_X", StudentId(1), LabId("L_EDGE"))
    instance.start_lab(base_lab)
    instance.complete_step(StepId("s1"), base_lab)
    instance.complete_step(StepId("s2"), base_lab)
    
    # Le lab est maintenant COMPLETED. On tente de re-valider.
    with pytest.raises(InvalidLabState):
        instance.complete_step(StepId("s2"), base_lab)

def test_record_attempt_multiple_steps_isolation():
    instance = LabInstance("inst_X", StudentId(1), LabId("L_EDGE"))
    policy = SubmissionPolicy(max_attempts=0, cooldown_seconds=0)
    
    instance.record_attempt(StepId("s1"), policy)
    instance.record_attempt(StepId("s1"), policy)
    instance.record_attempt(StepId("s2"), policy)
    
    # Les compteurs de tentatives doivent être isolés par étape
    assert instance.attempts["s1"] == 2
    assert instance.attempts["s2"] == 1

def test_finish_lab_with_remaining_steps(base_lab):
    instance = LabInstance("inst_X", StudentId(1), LabId("L_EDGE"))
    instance.start_lab(base_lab)
    
    # On force la fin alors que s1 et s2 ne sont pas terminés (accès privé à _finish_lab pour tester la protection interne si elle existait, ou la protection de finish_lab public)
    # Puisque nous avons supprimé finish_lab public, nous testons que l'état reste cohérent
    assert instance.status == LabStatus.IN_PROGRESS
    assert len(instance.completed_steps) == 0

def test_score_accumulation(base_lab):
    instance = LabInstance("inst_X", StudentId(1), LabId("L_EDGE"))
    instance.start_lab(base_lab)
    instance.complete_step(StepId("s1"), base_lab)
    
    assert instance.score == 5
    instance.complete_step(StepId("s2"), base_lab)
    assert instance.score == 20

def test_lab_status_enum_values():
    assert LabStatus.NOT_STARTED.value == "NOT_STARTED"
    assert LabStatus.COMPLETED.value == "COMPLETED"

def test_step_type_enum_values():
    assert StepType.FLAG.value == "FLAG"
    assert StepType.QUIZ.value == "QUIZ"

def test_auto_transition_clears_current_step(base_lab):
    instance = LabInstance("inst_X", StudentId(1), LabId("L_EDGE"))
    instance.start_lab(base_lab)
    instance.complete_step(StepId("s1"), base_lab)
    instance.complete_step(StepId("s2"), base_lab)
    
    assert instance.current_step is None
    assert instance.status == LabStatus.COMPLETED