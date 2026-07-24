import pytest
from domain.labs.exceptions import (
    MaxAttemptsReached,
    CooldownActive,
    InvalidSubmissionPolicy,
    InvalidLabTransition
)

def test_domain_exceptions_formatting():
    # Test MaxAttemptsReached (Correction des arguments et de exc_info)
    with pytest.raises(MaxAttemptsReached) as exc_info:
        raise MaxAttemptsReached(step_id="step_1", attempts_count=3, max_attempts=3)
    
    assert exc_info.value.attempts_count == 3
    assert exc_info.value.max_attempts == 3
    assert exc_info.value.step_id == "step_1"
    assert "Nombre maximum d'essais atteint (3/3) pour l'étape step_1" in str(exc_info.value)

    # Test CooldownActive
    with pytest.raises(CooldownActive) as exc_info:
        raise CooldownActive(step_id="step_1", remaining_seconds=42)
    
    assert exc_info.value.remaining_seconds == 42
    assert "Cooldown actif pour l'étape step_1" in str(exc_info.value)

    # Test InvalidSubmissionPolicy
    with pytest.raises(InvalidSubmissionPolicy) as exc_info:
        raise InvalidSubmissionPolicy()
    
    assert "La politique de soumission est invalide" in str(exc_info.value)