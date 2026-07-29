import pytest
from datetime import datetime, timezone, timedelta
from dataclasses import FrozenInstanceError

from domain.policies.attempt_policy import AttemptPolicy
from domain.entities.attempt import Attempt
from domain.value_objects.attempt_id import AttemptId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.correlation_id import CorrelationId
from domain.exceptions import LabLockedOutException, CooldownException


@pytest.fixture
def base_policy():
    return AttemptPolicy(max_attempts=3, cooldown_seconds=10, lockout_duration_minutes=15)

@pytest.fixture
def current_time():
    return datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

def create_attempt(att_id: str, minutes_offset: int, is_correct: bool = False) -> Attempt:
    """Helper pour générer des entités Attempt conformes."""
    base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return Attempt(
        attempt_id=AttemptId(att_id),
        objective_id=ObjectiveId("obj-1"),
        correlation_id=CorrelationId(f"corr-{att_id}"),
        timestamp=base_time + timedelta(minutes=minutes_offset),
        is_correct=is_correct
    )


def test_attempt_policy_allows_valid_attempt(base_policy, current_time):
    # Historique vide
    assert base_policy.can_attempt(history=[], current_time=current_time) is True
    
    # Historique avec une tentative ancienne (hors cooldown)
    old_attempt = create_attempt("old", minutes_offset=-5)
    assert base_policy.can_attempt(history=[old_attempt], current_time=current_time) is True


def test_attempt_policy_blocks_after_max_attempts(base_policy, current_time):
    # 3 échecs (atteint max_attempts)
    history = [
        create_attempt("fail-1", minutes_offset=-30),
        create_attempt("fail-2", minutes_offset=-20),
        create_attempt("fail-3", minutes_offset=-10)
    ]
    
    with pytest.raises(LabLockedOutException, match="Nombre maximum de tentatives atteint"):
        base_policy.can_attempt(history=history, current_time=current_time)


def test_attempt_policy_blocks_attempt_during_cooldown(base_policy, current_time):
    # Tentative il y a seulement 2 secondes (cooldown = 10s)
    recent_attempt = Attempt(
        attempt_id=AttemptId("recent"),
        objective_id=ObjectiveId("obj-1"),
        correlation_id=CorrelationId("corr-1"),
        timestamp=current_time - timedelta(seconds=2),
        is_correct=False
    )
    
    with pytest.raises(CooldownException, match="Veuillez patienter avant la prochaine tentative"):
        base_policy.can_attempt(history=[recent_attempt], current_time=current_time)


def test_attempt_policy_is_immutable(base_policy):
    with pytest.raises(FrozenInstanceError):
        base_policy.max_attempts = 5