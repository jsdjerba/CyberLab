import pytest
from datetime import timedelta, datetime
from dataclasses import FrozenInstanceError

# VOs (Déjà implémentés et verts)
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.attempt_id import AttemptId
from domain.value_objects.correlation_id import CorrelationId
from domain.value_objects.completion_time import CompletionTime

# Base Event
from domain.events.base_domain_event import BaseDomainEvent

# Événements (Ces imports échoueront en phase TDD)
from domain.events.lab_started import LabStarted
from domain.events.flag_submitted import FlagSubmitted
from domain.events.flag_rejected import FlagRejected
from domain.events.flag_validated import FlagValidated
from domain.events.objective_completed import ObjectiveCompleted
from domain.events.lab_locked_out import LabLockedOut
from domain.events.lab_completed import LabCompleted


# ==============================================================================
# FIXTURES RÉUTILISABLES (Value Objects validés)
# ==============================================================================
@pytest.fixture
def correlation_id(): return CorrelationId("req-001")

@pytest.fixture
def student_id(): return StudentId("student-1")

@pytest.fixture
def lab_id(): return LabId("lab-101")

@pytest.fixture
def objective_id(): return ObjectiveId("obj-root")

@pytest.fixture
def attempt_id(): return AttemptId("attempt-42")


# ==============================================================================
# TESTS SPÉCIFIQUES PAR ÉVÉNEMENT
# ==============================================================================

def test_lab_started_creation(correlation_id, student_id, lab_id):
    """Vérifie la création valide de LabStarted avec ses VOs."""
    event = LabStarted(
        correlation_id=correlation_id,
        student_id=student_id,
        lab_id=lab_id
    )
    assert event.student_id == student_id
    assert event.lab_id == lab_id

def test_flag_submitted_creation_and_absence_of_secret(correlation_id, student_id, lab_id, objective_id, attempt_id):
    """Vérifie que FlagSubmitted trace l'action, sans jamais stocker le flag soumis."""
    event = FlagSubmitted(
        correlation_id=correlation_id,
        student_id=student_id,
        lab_id=lab_id,
        objective_id=objective_id,
        attempt_id=attempt_id
    )
    assert event.attempt_id == attempt_id
    # Test critique de sécurité individuel
    assert not hasattr(event, 'flag')
    assert not hasattr(event, 'submitted_value')

def test_flag_rejected_creation(correlation_id, student_id, lab_id, objective_id):
    """Vérifie la création de FlagRejected avec sa raison métier."""
    event = FlagRejected(
        correlation_id=correlation_id,
        student_id=student_id,
        lab_id=lab_id,
        objective_id=objective_id,
        reason="Rate limit exceeded"
    )
    assert event.reason == "Rate limit exceeded"

def test_flag_validated_creation(correlation_id, student_id, lab_id, objective_id):
    """Vérifie la création de FlagValidated."""
    event = FlagValidated(
        correlation_id=correlation_id,
        student_id=student_id,
        lab_id=lab_id,
        objective_id=objective_id
    )
    assert event.objective_id == objective_id

def test_objective_completed_creation(correlation_id, student_id, lab_id, objective_id):
    """Vérifie la création de ObjectiveCompleted."""
    event = ObjectiveCompleted(
        correlation_id=correlation_id,
        student_id=student_id,
        lab_id=lab_id,
        objective_id=objective_id
    )
    assert event.objective_id == objective_id

def test_lab_locked_out_creation_and_validation(correlation_id, student_id, lab_id):
    """Vérifie la création de LabLockedOut et le refus des durées négatives."""
    event = LabLockedOut(
        correlation_id=correlation_id,
        student_id=student_id,
        lab_id=lab_id,
        lockout_duration=timedelta(minutes=15)
    )
    assert event.lockout_duration.total_seconds() == 900
    
    # Validation du contrat métier sur la durée
    with pytest.raises(ValueError, match="La durée de blocage ne peut pas être négative"):
        LabLockedOut(
            correlation_id=correlation_id,
            student_id=student_id,
            lab_id=lab_id,
            lockout_duration=timedelta(minutes=-5)
        )

def test_lab_completed_creation(correlation_id, student_id, lab_id):
    """Vérifie la création de LabCompleted et son VO spécifique."""
    completion_time = CompletionTime(duration=timedelta(minutes=45))
    event = LabCompleted(
        correlation_id=correlation_id,
        student_id=student_id,
        lab_id=lab_id,
        completion_time=completion_time
    )
    assert event.completion_time == completion_time


# ==============================================================================
# TESTS TRANSVERSAUX (CONTRAT D'ARCHITECTURE GLOBAL)
# ==============================================================================

def get_all_events(correlation_id, student_id, lab_id, objective_id, attempt_id):
    """Générateur utilitaire pour instancier tous les événements à tester."""
    return [
        LabStarted(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id),
        FlagSubmitted(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id, objective_id=objective_id, attempt_id=attempt_id),
        FlagRejected(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id, objective_id=objective_id, reason="Bad format"),
        FlagValidated(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id, objective_id=objective_id),
        ObjectiveCompleted(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id, objective_id=objective_id),
        LabLockedOut(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id, lockout_duration=timedelta(minutes=5)),
        LabCompleted(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id, completion_time=CompletionTime(timedelta(hours=1)))
    ]

def test_all_learning_events_inherit_base_domain_event(correlation_id, student_id, lab_id, objective_id, attempt_id):
    events = get_all_events(correlation_id, student_id, lab_id, objective_id, attempt_id)
    for event in events:
        assert isinstance(event, BaseDomainEvent), f"{type(event).__name__} doit hériter de BaseDomainEvent"
        assert hasattr(event, 'timestamp'), f"{type(event).__name__} doit posséder un timestamp automatique"
        assert isinstance(event.timestamp, datetime)

def test_all_learning_events_are_immutable(correlation_id, student_id, lab_id, objective_id, attempt_id):
    events = get_all_events(correlation_id, student_id, lab_id, objective_id, attempt_id)
    for event in events:
        with pytest.raises(FrozenInstanceError):
            event.student_id = StudentId("hacked-id")

def test_all_learning_events_enforce_ddd_typing(correlation_id, student_id, lab_id, objective_id, attempt_id):
    events = get_all_events(correlation_id, student_id, lab_id, objective_id, attempt_id)
    for event in events:
        assert isinstance(event.correlation_id, CorrelationId)
        assert isinstance(event.student_id, StudentId)
        assert isinstance(event.lab_id, LabId)
        if hasattr(event, 'objective_id'):
            assert isinstance(event.objective_id, ObjectiveId)

def test_all_learning_events_equality_by_value(correlation_id, student_id, lab_id):
    event1 = LabStarted(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id)
    event2 = LabStarted(correlation_id=correlation_id, student_id=student_id, lab_id=lab_id)
    
    assert event1 == event2
    assert id(event1) != id(event2)

def test_security_no_learning_event_contains_secret_flag(correlation_id, student_id, lab_id, objective_id, attempt_id):
    """
    Test d'audit de sécurité : S'assure qu'absolument aucun événement 
    ne fait transiter de propriétés interdites pouvant fuiter dans l'EventBus ou les Logs.
    """
    events = get_all_events(correlation_id, student_id, lab_id, objective_id, attempt_id)
    forbidden_attributes = ['flag', 'plaintext_flag', 'raw_flag', 'submitted_flag']
    
    for event in events:
        for forbidden in forbidden_attributes:
            assert not hasattr(event, forbidden), \
                f"SÉCURITÉ COMPROMISE : L'événement {type(event).__name__} contient l'attribut interdit '{forbidden}'."