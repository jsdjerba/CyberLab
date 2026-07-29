import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError
from domain.events.base_domain_event import BaseDomainEvent
from domain.events.lab_started import LabStarted
from domain.events.flag_submitted import FlagSubmitted
from domain.events.flag_validated import FlagValidated
from domain.events.lab_completed import LabCompleted

def test_learning_events_inherit_base_domain_event_and_are_immutable():
    events_classes = [
        LabStarted(correlation_id="req-1", student_id="s1", lab_id="l1"),
        FlagSubmitted(correlation_id="req-1", student_id="s1", lab_id="l1", attempt_number=1),
        FlagValidated(correlation_id="req-1", student_id="s1", lab_id="l1", attempt_number=1),
        LabCompleted(correlation_id="req-1", student_id="s1", lab_id="l1", completion_time=datetime.utcnow())
    ]
    
    for event in events_classes:
        assert isinstance(event, BaseDomainEvent)
        assert isinstance(event.correlation_id, str)
        assert isinstance(event.timestamp, datetime)
        
        # Vérification de l'immuabilité (frozen)
        with pytest.raises(FrozenInstanceError):
            event.correlation_id = "mutated-id"

def test_learning_events_payloads_structure():
    now = datetime.utcnow()
    
    started = LabStarted(correlation_id="c-1", student_id="stu-1", lab_id="lab-1")
    assert started.student_id == "stu-1"
    assert started.lab_id == "lab-1"
    
    submitted = FlagSubmitted(correlation_id="c-2", student_id="stu-1", lab_id="lab-1", attempt_number=2)
    assert submitted.student_id == "stu-1"
    assert submitted.lab_id == "lab-1"
    assert submitted.attempt_number == 2
    # Vérification stricte : FlagSubmitted ne doit PAS posséder de champ is_correct
    assert not hasattr(submitted, "is_correct")
    
    validated = FlagValidated(correlation_id="c-3", student_id="stu-1", lab_id="lab-1", attempt_number=2)
    assert validated.student_id == "stu-1"
    assert validated.lab_id == "lab-1"
    assert validated.attempt_number == 2
    
    completed = LabCompleted(correlation_id="c-4", student_id="stu-1", lab_id="lab-1", completion_time=now)
    assert completed.student_id == "stu-1"
    assert completed.lab_id == "lab-1"
    assert completed.completion_time == now