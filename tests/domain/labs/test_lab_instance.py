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
from domain.labs.exceptions import (
    InvalidLabState, InvalidStepTransition, StepAlreadyCompleted, StepNotFound
)
from domain.labs.events.lab_started import LabStarted
from domain.labs.events.step_completed import StepCompleted
from domain.labs.events.lab_finished import LabFinished

@pytest.fixture
def sample_lab():
    step1 = Step(StepId("s1"), StepType.INFO, "Intro", 0)
    step2 = Step(StepId("s2"), StepType.FLAG, "Flag 1", 10)
    return Lab(LabId("L1"), "Test", "Desc", "Easy", 30, [step1, step2])

@pytest.fixture
def empty_lab():
    return Lab(LabId("L2"), "Empty", "Desc", "Easy", 30, [])

def test_create_instance():
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    assert instance.status == LabStatus.NOT_STARTED
    assert instance.current_step is None

def test_invalid_student_id():
    with pytest.raises(Exception):
        StudentId(0)

def test_start_lab_success(sample_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.start_lab(sample_lab)
    
    assert instance.status == LabStatus.IN_PROGRESS
    assert instance.current_step == StepId("s1")
    
    events = instance.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], LabStarted)

def test_start_lab_already_started(sample_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.start_lab(sample_lab)
    with pytest.raises(InvalidLabState):
        instance.start_lab(sample_lab)

def test_start_lab_empty_steps(empty_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L2"))
    with pytest.raises(InvalidLabState):
        instance.start_lab(empty_lab)

def test_complete_step_success(sample_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.start_lab(sample_lab)
    instance.pull_events() # clear start event
    
    instance.complete_step(StepId("s1"), sample_lab)
    
    assert instance.score == 0
    assert instance.current_step == StepId("s2")
    assert StepId("s1") in instance.completed_steps
    
    events = instance.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], StepCompleted)
    assert events[0].step_id == "s1"

def test_complete_step_auto_finish(sample_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.start_lab(sample_lab)
    
    instance.complete_step(StepId("s1"), sample_lab)
    instance.complete_step(StepId("s2"), sample_lab)
    
    assert instance.status == LabStatus.COMPLETED
    assert instance.current_step is None
    assert instance.score == 10
    
    # Validation du dernier événement
    events = instance.pull_events()
    assert isinstance(events[-1], LabFinished)
    assert events[-1].final_score == 10

def test_complete_step_wrong_step(sample_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.start_lab(sample_lab)
    
    with pytest.raises(InvalidStepTransition):
        instance.complete_step(StepId("s2"), sample_lab) # Attendu s1

def test_complete_step_already_completed(sample_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.start_lab(sample_lab)
    instance.complete_step(StepId("s1"), sample_lab)
    
    with pytest.raises(StepAlreadyCompleted):
        instance.complete_step(StepId("s1"), sample_lab)

def test_pull_events_clears_queue(sample_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.start_lab(sample_lab)
    
    events1 = instance.pull_events()
    assert len(events1) == 1
    
    events2 = instance.pull_events()
    assert len(events2) == 0

def test_record_attempt():
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    policy = SubmissionPolicy(max_attempts=3, cooldown_seconds=0)
    
    instance.record_attempt(StepId("s1"), policy)
    instance.record_attempt(StepId("s1"), policy)
    
    assert instance.attempts["s1"] == 2