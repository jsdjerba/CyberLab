import pytest
from domain.labs.entities.lab import Lab
from domain.labs.entities.step import Step
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.step_type import StepType
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.lab_status import LabStatus
from domain.labs.value_objects.lifecycle_context import LifecycleContext
from domain.labs.services.lifecycle_service import LabLifecycleService
from domain.labs.exceptions import LabNotPublished, InvalidLabTransition, InvalidLabState
from domain.labs.events.lab_started import LabStarted

class FakeLab:
    """Objet de test simulant un Lab avec un statut de publication sans violer le domaine."""
    def __init__(self, lab_id: LabId, steps: list, is_published: bool):
        self.id = lab_id
        self.steps = steps
        self.is_published = is_published

@pytest.fixture
def lifecycle_service():
    return LabLifecycleService()

@pytest.fixture
def lifecycle_context():
    return LifecycleContext(student_id=StudentId(1))

@pytest.fixture
def published_lab():
    step1 = Step(StepId("s1"), StepType.INFO, "Intro", 0)
    return FakeLab(LabId("L1"), [step1], is_published=True)

@pytest.fixture
def unpublished_lab():
    step1 = Step(StepId("s1"), StepType.INFO, "Intro", 0)
    return FakeLab(LabId("L2"), [step1], is_published=False)

def test_start_lab_success(lifecycle_service, published_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    
    lifecycle_service.start_lab(instance, published_lab, lifecycle_context)
    
    assert instance.status == LabStatus.IN_PROGRESS
    assert instance.current_step == StepId("s1")
    events = instance.pull_events()
    assert any(isinstance(e, LabStarted) for e in events)

def test_start_lab_unpublished_lab(lifecycle_service, unpublished_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L2"))
    
    with pytest.raises(LabNotPublished):
        lifecycle_service.start_lab(instance, unpublished_lab, lifecycle_context)

def test_invalid_transition_completed_to_running(lifecycle_service, published_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    instance.status = LabStatus.COMPLETED
    
    with pytest.raises(InvalidLabTransition):
        lifecycle_service.start_lab(instance, published_lab, lifecycle_context)

def test_pause_running_lab(lifecycle_service, published_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    lifecycle_service.start_lab(instance, published_lab, lifecycle_context)
    
    if not hasattr(instance, "pause"):
        setattr(instance, "pause", lambda: setattr(instance, "status", LabStatus.PAUSED))
        
    lifecycle_service.pause_lab(instance, lifecycle_context)
    assert instance.status == LabStatus.PAUSED

def test_abandon_running_lab(lifecycle_service, published_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    lifecycle_service.start_lab(instance, published_lab, lifecycle_context)
    
    if not hasattr(instance, "abandon"):
        setattr(instance, "abandon", lambda: setattr(instance, "status", LabStatus.ABANDONED))

    lifecycle_service.abandon_lab(instance, lifecycle_context)
    assert instance.status == LabStatus.ABANDONED

def test_complete_finished_lab(lifecycle_service, published_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    lifecycle_service.start_lab(instance, published_lab, lifecycle_context)
    
    instance.complete_step(StepId("s1"), published_lab)
    
    if not hasattr(instance, "complete"):
        setattr(instance, "complete", lambda: setattr(instance, "status", LabStatus.COMPLETED))

    lifecycle_service.complete_lab(instance, published_lab, lifecycle_context)
    assert instance.status == LabStatus.COMPLETED

def test_pause_running_lab(lifecycle_service, published_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    lifecycle_service.start_lab(instance, published_lab, lifecycle_context)
    
    lifecycle_service.pause_lab(instance, lifecycle_context)
    assert instance.status == LabStatus.PAUSED

def test_abandon_running_lab(lifecycle_service, published_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    lifecycle_service.start_lab(instance, published_lab, lifecycle_context)

    lifecycle_service.abandon_lab(instance, lifecycle_context)
    assert instance.status == LabStatus.ABANDONED

def test_complete_finished_lab(lifecycle_service, published_lab, lifecycle_context):
    instance = LabInstance("inst_1", StudentId(1), LabId("L1"))
    lifecycle_service.start_lab(instance, published_lab, lifecycle_context)
    
    instance.complete_step(StepId("s1"), published_lab)

    lifecycle_service.complete_lab(instance, published_lab, lifecycle_context)
    assert instance.status == LabStatus.COMPLETED