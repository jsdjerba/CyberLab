import pytest
from datetime import datetime
from dataclasses import dataclass, FrozenInstanceError
from domain.events.base_domain_event import BaseDomainEvent
from domain.events.score_updated import ScoreUpdated

# Création d'un événement factice héritant de BaseDomainEvent pour le test
@dataclass(frozen=True, kw_only=True)
class DummyEvent(BaseDomainEvent):
    student_id: str
    lab_id: str

def test_base_domain_event_initializes_with_correlation_id_and_timestamp():
    correlation_id = "req-uuid-1234"
    event = DummyEvent(correlation_id=correlation_id, student_id="stu-1", lab_id="lab-1")
    
    # Vérification des métadonnées
    assert event.correlation_id == "req-uuid-1234"
    assert isinstance(event.timestamp, datetime)
    
    # Vérification du payload métier
    assert event.student_id == "stu-1"
    assert event.lab_id == "lab-1"

def test_base_domain_event_is_immutable():
    event = DummyEvent(correlation_id="req-uuid-1234", student_id="stu-1", lab_id="lab-1")
    
    # Vérifie que la dataclass est bien figée (frozen)
    with pytest.raises(FrozenInstanceError):
        event.correlation_id = "new-uuid"

def test_score_updated_event_is_immutable():
    event = ScoreUpdated(
        correlation_id="req-uuid", 
        student_id="stu-1", 
        added_points=50, 
        new_total_score=50
    )
    
    # Vérifie qu'un événement métier réel ne peut pas être muté après sa création
    with pytest.raises(FrozenInstanceError):
        event.new_total_score = 100