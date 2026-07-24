import pytest
from unittest.mock import MagicMock
from application.labs.services.step_validation_service import StepValidationService
from domain.labs.entities.lab import Lab
from domain.labs.entities.step import Step
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.step_type import StepType
from domain.labs.exceptions import InvalidStepTransition

@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.lab_instances = MagicMock()
    uow.labs = MagicMock()
    return uow

@pytest.fixture
def mock_flag_validator():
    return MagicMock()

@pytest.fixture
def mock_publisher():
    return MagicMock()

@pytest.fixture
def validation_service(mock_uow, mock_flag_validator, mock_publisher):
    return StepValidationService(
        uow=mock_uow,
        flag_validator=mock_flag_validator,
        publisher=mock_publisher
    )

@pytest.fixture
def sample_lab():
    step1 = Step(StepId("s1"), StepType.FLAG, "Flag 1", 10)
    step2 = Step(StepId("s2"), StepType.FLAG, "Flag 2", 20)
    return Lab(LabId("L1"), "Test Lab", "Desc", "Easy", 60, [step1, step2])

@pytest.fixture
def started_instance(sample_lab):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.start_lab(sample_lab)
    instance.pull_events()
    return instance

def test_submit_correct_flag(validation_service, mock_uow, mock_flag_validator, sample_lab, started_instance):
    mock_uow.labs.get_by_id.return_value = sample_lab
    mock_uow.lab_instances.get_by_student_and_lab.return_value = started_instance
    mock_flag_validator.validate.return_value = True
    
    result = validation_service.submit_flag(
        student_id_value=1,
        lab_id_value="L1",
        step_id_value="s1",
        submitted_flag="FLAG{123}"
    )
    
    assert result.success is True
    assert started_instance.current_step == StepId("s1") or started_instance.current_step == StepId("s2")
    mock_uow.commit.assert_called_once()

def test_submit_wrong_flag(validation_service, mock_uow, mock_flag_validator, sample_lab, started_instance):
    mock_uow.labs.get_by_id.return_value = sample_lab
    mock_uow.lab_instances.get_by_student_and_lab.return_value = started_instance
    mock_flag_validator.validate.return_value = False
    
    result = validation_service.submit_flag(
        student_id_value=1,
        lab_id_value="L1",
        step_id_value="s1",
        submitted_flag="WRONG"
    )
    
    assert result.success is False
    assert started_instance.current_step == StepId("s1")
    assert started_instance.get_attempt_count(StepId("s1")) == 1
    mock_uow.commit.assert_called_once()

def test_lab_not_found(validation_service, mock_uow, started_instance):
    mock_uow.labs.get_by_id.return_value = None
    mock_uow.lab_instances.get_by_student_and_lab.return_value = started_instance
    
    with pytest.raises(Exception):
        validation_service.submit_flag(1, "L1", "s1", "FLAG")

def test_instance_not_found(validation_service, mock_uow, sample_lab):
    mock_uow.labs.get_by_id.return_value = sample_lab
    mock_uow.lab_instances.get_by_student_and_lab.return_value = None
    
    with pytest.raises(Exception):
        validation_service.submit_flag(1, "L1", "s1", "FLAG")

def test_invalid_step_transition(validation_service, mock_uow, sample_lab, started_instance):
    mock_uow.labs.get_by_id.return_value = sample_lab
    mock_uow.lab_instances.get_by_student_and_lab.return_value = started_instance
    
    with pytest.raises(InvalidStepTransition):
        validation_service.submit_flag(1, "L1", "s2", "FLAG{456}")

def test_last_step_finishes_lab(validation_service, mock_uow, mock_flag_validator, sample_lab, started_instance):
    started_instance.complete_step(StepId("s1"), sample_lab) 
    
    mock_uow.labs.get_by_id.return_value = sample_lab
    mock_uow.lab_instances.get_by_student_and_lab.return_value = started_instance
    mock_flag_validator.validate.return_value = True
    
    result = validation_service.submit_flag(
        student_id_value=1,
        lab_id_value="L1",
        step_id_value="s2",
        submitted_flag="FLAG{456}"
    )
    
    assert result.success is True
    assert started_instance.status.value == "COMPLETED"
    assert started_instance.current_step is None

def test_publish_after_commit(validation_service, mock_uow, mock_flag_validator, mock_publisher, sample_lab, started_instance):
    mock_uow.labs.get_by_id.return_value = sample_lab
    mock_uow.lab_instances.get_by_student_and_lab.return_value = started_instance
    mock_flag_validator.validate.return_value = True
    
    validation_service.submit_flag(1, "L1", "s1", "FLAG{123}")
    
    mock_uow.commit.assert_called_once()
    mock_publisher.publish.assert_called()