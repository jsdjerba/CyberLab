import pytest
from domain.labs.entities.lab import Lab
from domain.labs.entities.step import Step
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.step_type import StepType
from domain.labs.exceptions import LabDomainError, StepNotFound

def test_valid_lab_id():
    lab_id = LabId("HTTP_01")
    assert lab_id.value == "HTTP_01"

def test_invalid_lab_id():
    with pytest.raises(LabDomainError):
        LabId("HTTP-01!") # Caractères spéciaux interdits

def test_valid_step_id():
    step_id = StepId("step-1_auth")
    assert step_id.value == "step-1_auth"

def test_invalid_step_id():
    with pytest.raises(LabDomainError):
        StepId("step 1") # Espace interdit

def test_lab_total_points():
    step1 = Step(StepId("s1"), StepType.INFO, "Intro", 0)
    step2 = Step(StepId("s2"), StepType.FLAG, "Flag 1", 10)
    step3 = Step(StepId("s3"), StepType.FLAG, "Flag 2", 20)
    lab = Lab(LabId("L1"), "Test Lab", "Desc", "Easy", 30, [step1, step2, step3])
    
    assert lab.total_points() == 30
    assert lab.number_of_steps() == 3

def test_lab_get_step_success():
    step1 = Step(StepId("s1"), StepType.INFO, "Intro", 0)
    lab = Lab(LabId("L1"), "Test Lab", "Desc", "Easy", 30, [step1])
    
    retrieved = lab.get_step(StepId("s1"))
    assert retrieved == step1

def test_lab_get_step_not_found():
    step1 = Step(StepId("s1"), StepType.INFO, "Intro", 0)
    lab = Lab(LabId("L1"), "Test Lab", "Desc", "Easy", 30, [step1])
    
    with pytest.raises(StepNotFound):
        lab.get_step(StepId("s2"))