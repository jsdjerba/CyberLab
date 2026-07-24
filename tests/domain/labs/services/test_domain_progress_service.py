import pytest
from dataclasses import FrozenInstanceError

from domain.labs.services.progress_service import ProgressService
from domain.labs.entities.lab import Lab
from domain.labs.entities.step import Step
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.step_type import StepType

# Identifiants valides respectant le regex ^[a-zA-Z0-9_]+$ (sans tirets)
VALID_LAB_ID = "VALID_LAB_123"
EMPTY_LAB_ID = "EMPTY_LAB_000"

@pytest.fixture
def progress_service():
    return ProgressService()

@pytest.fixture
def base_lab():
    return Lab(
        id=LabId(VALID_LAB_ID),
        title="Progression Lab",
        description="Testing progress",
        difficulty="EASY",
        duration=60,
        steps=[
            Step(StepId("step_1"), StepType.FLAG, "Flag 1", 10),
            Step(StepId("step_2"), StepType.QUIZ, "Quiz 1", 10),
            Step(StepId("step_3"), StepType.FLAG, "Flag 2", 10),
            Step(StepId("step_4"), StepType.FLAG, "Flag 3", 10),
        ]
    )

@pytest.fixture
def instance(base_lab):
    inst = LabInstance("inst_1", StudentId(1), LabId(VALID_LAB_ID))
    inst.start_lab(base_lab)
    return inst

def test_evaluate_empty_lab(progress_service):
    empty_lab = Lab(LabId(EMPTY_LAB_ID), "Empty", "Desc", "EASY", 10, [])
    inst = LabInstance("inst_empty", StudentId(1), LabId(EMPTY_LAB_ID))
    
    report = progress_service.evaluate_progress(inst, empty_lab)
    
    assert report.completion_percentage == 100.0
    assert report.is_finished is True
    assert report.total_steps == 0
    assert report.has_remaining_steps is False
    assert report.completed_steps == ()
    assert report.remaining_steps == ()
    assert report.next_available_steps == ()

def test_evaluate_one_step_lab(progress_service):
    lab = Lab(LabId(VALID_LAB_ID), "Title", "Desc", "EASY", 10, [Step(StepId("s1"), StepType.FLAG, "F1", 10)])
    inst = LabInstance("inst_1", StudentId(1), LabId(VALID_LAB_ID))
    inst.start_lab(lab)
    
    report_start = progress_service.evaluate_progress(inst, lab)
    assert report_start.completion_percentage == 0.0
    
    inst.complete_step(StepId("s1"), lab)
    report_end = progress_service.evaluate_progress(inst, lab)
    
    assert report_end.completion_percentage == 100.0
    assert report_end.is_finished is True
    assert report_end.total_steps == 1
    assert report_end.has_remaining_steps is False

def test_evaluate_zero_percent_progress(progress_service, instance, base_lab):
    report = progress_service.evaluate_progress(instance, base_lab)
    
    assert report.completion_percentage == 0.0
    assert report.is_finished is False
    assert report.total_steps == 4
    assert report.has_remaining_steps is True
    assert report.next_available_steps == (StepId("step_1"),)

def test_evaluate_partial_progress(progress_service, instance, base_lab):
    instance.complete_step(StepId("step_1"), base_lab)
    instance.complete_step(StepId("step_2"), base_lab)
    
    report = progress_service.evaluate_progress(instance, base_lab)
    
    assert report.completion_percentage == 50.0
    assert report.is_finished is False
    assert report.total_steps == 4
    assert report.has_remaining_steps is True
    assert report.completed_steps == (StepId("step_1"), StepId("step_2"))
    assert report.remaining_steps == (StepId("step_3"), StepId("step_4"))
    assert report.next_available_steps == (StepId("step_3"),)

def test_evaluate_full_progress(progress_service, instance, base_lab):
    for step in base_lab.get_steps():
        instance.complete_step(step.id, base_lab)
        
    report = progress_service.evaluate_progress(instance, base_lab)
    
    assert report.completion_percentage == 100.0
    assert report.is_finished is True
    assert report.has_remaining_steps is False
    assert report.remaining_steps == ()
    assert report.next_available_steps == ()

def test_robustness_unknown_steps(progress_service, base_lab):
    inst = LabInstance("inst_1", StudentId(1), LabId(VALID_LAB_ID))
    inst.start_lab(base_lab)
    
    inst._completed_steps = [StepId("step_1"), StepId("unknown_step")]
    
    report = progress_service.evaluate_progress(inst, base_lab)
    
    assert report.completion_percentage == 25.0
    assert report.completed_count == 1
    assert report.completed_steps == (StepId("step_1"),)

def test_robustness_duplicated_steps(progress_service, base_lab):
    inst = LabInstance("inst_1", StudentId(1), LabId(VALID_LAB_ID))
    inst.start_lab(base_lab)
    
    inst._completed_steps = [StepId("step_1"), StepId("step_1")]
    
    report = progress_service.evaluate_progress(inst, base_lab)
    
    assert report.completion_percentage == 25.0
    assert report.completed_count == 1
    assert report.completed_steps == (StepId("step_1"),)

def test_progress_report_is_immutable(progress_service, instance, base_lab):
    report = progress_service.evaluate_progress(instance, base_lab)
    
    with pytest.raises(FrozenInstanceError):
        report.completion_percentage = 99.0

def test_progress_report_is_hashable(progress_service, instance, base_lab):
    report = progress_service.evaluate_progress(instance, base_lab)
    
    test_dict = {report: "valid"}
    assert test_dict[report] == "valid"

def test_no_side_effects_on_instance(progress_service, instance, base_lab):
    initial_score = instance.score
    initial_completed = tuple(instance.get_completed_steps())
    
    progress_service.evaluate_progress(instance, base_lab)
    
    assert instance.score == initial_score
    assert tuple(instance.get_completed_steps()) == initial_completed