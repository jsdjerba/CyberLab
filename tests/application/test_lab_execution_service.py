import pytest
from application.labs.services.lab_execution_service import LabExecutionService
from application.labs.exceptions import LabNotFoundError
from domain.labs.entities.lab import Lab
from domain.labs.entities.step import Step
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.step_type import StepType
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.lab_status import LabStatus
from domain.labs.exceptions import InvalidLabState
from domain.labs.events.lab_started import LabStarted

from infrastructure.fakes.fake_unit_of_work import FakeUnitOfWork
from infrastructure.fakes.fake_event_publisher import FakeEventPublisher

@pytest.fixture
def setup_data():
    uow = FakeUnitOfWork()
    publisher = FakeEventPublisher()
    
    step1 = Step(StepId("s1"), StepType.INFO, "Intro", 10)
    lab = Lab(LabId("L1"), "Test Lab", "Desc", "Easy", 30, [step1])
    uow.labs.add(lab)
    
    service = LabExecutionService(uow, publisher)
    return service, uow, publisher, lab

# TEST 1 : start_lab_success
def test_start_lab_success(setup_data):
    service, uow, publisher, lab = setup_data
    
    instance_id = service.start_lab(1, "L1")
    
    assert uow.committed is True
    assert uow.rolled_back is False
    
    instance = uow.lab_instances.get_by_student_and_lab(StudentId(1), LabId("L1"))
    assert instance is not None
    assert instance.id == instance_id
    assert instance.status == LabStatus.IN_PROGRESS
    assert instance.current_step == StepId("s1")
    
    assert len(publisher.published_events) == 1
    assert isinstance(publisher.published_events[0], LabStarted)
    assert publisher.published_events[0].lab_instance_id == instance_id

# TEST 2 : lab_not_found
def test_lab_not_found(setup_data):
    service, uow, publisher, _ = setup_data
    
    with pytest.raises(LabNotFoundError):
        service.start_lab(1, "UNKNOWN")
        
    assert uow.committed is False
    assert uow.rolled_back is True
    assert len(publisher.published_events) == 0

# TEST 3 : already_started_lab
def test_already_started_lab(setup_data):
    service, uow, publisher, _ = setup_data
    
    # Premier appel réussi
    service.start_lab(1, "L1")
    
    # Réinitialisation des marqueurs du FakeUoW pour le second test
    uow.committed = False 
    uow.rolled_back = False
    
    # Deuxième appel
    with pytest.raises(InvalidLabState):
        service.start_lab(1, "L1")
        
    assert uow.committed is False
    assert uow.rolled_back is True

# TEST 4 : event_published_after_commit
def test_event_published_after_commit(setup_data):
    service, uow, publisher, _ = setup_data
    
    execution_order = []
    
    # Remplacement temporaire (Monkey patching) pour tracker l'ordre d'exécution
    original_commit = uow.commit
    def tracking_commit():
        execution_order.append("COMMIT")
        original_commit()
    uow.commit = tracking_commit
    
    original_publish = publisher.publish
    def tracking_publish(event):
        execution_order.append("PUBLISH")
        original_publish(event)
    publisher.publish = tracking_publish
    
    service.start_lab(1, "L1")
    
    assert execution_order == ["COMMIT", "PUBLISH"]

# TEST 5 : repository_save_failure
def test_repository_save_failure(setup_data):
    service, uow, publisher, _ = setup_data
    
    # Remplacement temporaire pour forcer une erreur
    def failing_save(instance):
        raise RuntimeError("DB Connection Lost")
    uow.lab_instances.save = failing_save
    
    with pytest.raises(RuntimeError):
        service.start_lab(1, "L1")
        
    assert uow.committed is False
    assert uow.rolled_back is True
    assert len(publisher.published_events) == 0