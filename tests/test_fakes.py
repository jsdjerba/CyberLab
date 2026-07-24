import pytest
from domain.labs.entities.lab import Lab
from domain.labs.entities.step import Step
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.step_type import StepType
from domain.labs.value_objects.student_id import StudentId
from domain.labs.events.lab_started import LabStarted
from domain.labs.events.step_completed import StepCompleted
from application.common.interfaces.event_publisher import EventHandler

from infrastructure.fakes.fake_lab_repository import FakeLabRepository
from infrastructure.fakes.fake_lab_instance_repository import FakeLabInstanceRepository
from infrastructure.fakes.fake_unit_of_work import FakeUnitOfWork
from infrastructure.fakes.fake_event_publisher import FakeEventPublisher
from infrastructure.fakes.fake_flag_validator import FakeFlagValidator

@pytest.fixture
def sample_lab():
    step1 = Step(StepId("s1"), StepType.FLAG, "Flag 1", 10)
    return Lab(LabId("L1"), "Test Lab", "Desc", "Easy", 30, [step1])

@pytest.fixture
def sample_lab_instance():
    return LabInstance("inst_1", StudentId(1), LabId("L1"))

# --- FakeLabRepository Tests ---

def test_fake_lab_repo_save_retrieve(sample_lab):
    repo = FakeLabRepository()
    repo.add(sample_lab)
    
    retrieved = repo.get_by_id(LabId("L1"))
    assert retrieved is not None
    assert retrieved.id.value == "L1"

def test_fake_lab_repo_missing():
    repo = FakeLabRepository()
    retrieved = repo.get_by_id(LabId("UNKNOWN"))
    assert retrieved is None

# --- FakeLabInstanceRepository Tests ---

def test_fake_instance_repo_save_retrieve(sample_lab_instance):
    repo = FakeLabInstanceRepository()
    repo.save(sample_lab_instance)
    
    retrieved = repo.get_by_student_and_lab(StudentId(1), LabId("L1"))
    assert retrieved is not None
    assert retrieved.id == "inst_1"

def test_fake_instance_repo_isolation():
    repo = FakeLabInstanceRepository()
    inst1 = LabInstance("inst_1", StudentId(1), LabId("L1"))
    inst2 = LabInstance("inst_2", StudentId(2), LabId("L1"))
    
    repo.save(inst1)
    repo.save(inst2)
    
    retrieved_1 = repo.get_by_student_and_lab(StudentId(1), LabId("L1"))
    retrieved_2 = repo.get_by_student_and_lab(StudentId(2), LabId("L1"))
    
    assert retrieved_1.id == "inst_1"
    assert retrieved_2.id == "inst_2"

def test_fake_instance_repo_missing():
    repo = FakeLabInstanceRepository()
    retrieved = repo.get_by_student_and_lab(StudentId(99), LabId("L1"))
    assert retrieved is None

# --- FakeUnitOfWork Tests ---

def test_fake_uow_commit():
    uow = FakeUnitOfWork()
    with uow:
        uow.commit()
    assert uow.committed is True
    assert uow.rolled_back is False

def test_fake_uow_rollback_on_exception():
    uow = FakeUnitOfWork()
    
    with pytest.raises(ValueError):
        with uow:
            raise ValueError("Something went wrong")
            uow.commit()
            
    assert uow.committed is False
    assert uow.rolled_back is True

def test_fake_uow_repositories_accessible():
    uow = FakeUnitOfWork()
    assert hasattr(uow, 'labs')
    assert hasattr(uow, 'lab_instances')

# --- FakeEventPublisher Tests ---

class MockHandler(EventHandler):
    def __init__(self):
        self.handled_events = []
        
    def handle(self, event):
        self.handled_events.append(event)

def test_fake_publisher_records_events():
    publisher = FakeEventPublisher()
    event = LabStarted(lab_instance_id="inst_1")
    
    publisher.publish(event)
    
    assert len(publisher.published_events) == 1
    assert publisher.published_events[0] == event

def test_fake_publisher_dispatches_to_subscribers():
    publisher = FakeEventPublisher()
    handler = MockHandler()
    
    publisher.subscribe(LabStarted, handler)
    
    event1 = LabStarted(lab_instance_id="inst_1")
    event2 = StepCompleted(lab_instance_id="inst_1", step_id="s1", score_awarded=10)
    
    publisher.publish(event1)
    publisher.publish(event2)
    
    assert len(handler.handled_events) == 1
    assert handler.handled_events[0] == event1

# --- FakeFlagValidator Tests ---

def test_fake_flag_validator(sample_lab):
    step = sample_lab.steps[0]
    validator = FakeFlagValidator(expected_flag="CTF{SUCCESS}")
    
    assert validator.validate(step, "CTF{SUCCESS}") is True
    assert validator.validate(step, "CTF{FAILED}") is False