import pytest
from application.labs.interfaces.lab_repository import LabRepository
from application.labs.interfaces.lab_instance_repository import LabInstanceRepository
from application.labs.interfaces.flag_validator import FlagValidator
from application.common.interfaces.unit_of_work import UnitOfWork
from application.common.interfaces.event_publisher import EventPublisher, EventHandler
from application.labs.results.lab_progress_result import LabProgressResult

def test_interfaces_cannot_be_instantiated():
    """Vérifie que les ports sont bien abstraits et nécessitent une implémentation."""
    with pytest.raises(TypeError):
        LabRepository()
    with pytest.raises(TypeError):
        LabInstanceRepository()
    with pytest.raises(TypeError):
        FlagValidator()
    with pytest.raises(TypeError):
        UnitOfWork()
    with pytest.raises(TypeError):
        EventPublisher()
    with pytest.raises(TypeError):
        EventHandler()

class FakeFlagValidator(FlagValidator):
    """Fake Strategy pour tester le contrat du port FlagValidator."""
    def __init__(self, expected_flag: str):
        self.expected = expected_flag

    def validate(self, step, submitted_flag: str) -> bool:
        return submitted_flag == self.expected

def test_fake_flag_validator_strategy():
    """Vérifie le fonctionnement de la validation par stratégie."""
    validator = FakeFlagValidator("CTF{OK}")
    
    # Simule une étape sans mocker tout le domaine
    assert validator.validate(step=None, submitted_flag="CTF{OK}") is True
    assert validator.validate(step=None, submitted_flag="WRONG") is False

def test_lab_progress_result_immutability():
    """Vérifie que notre Result Model (DTO interne) est bien immuable."""
    result = LabProgressResult(
        lab_id="HTTP_01",
        student_id=42,
        status="IN_PROGRESS",
        current_step="step-1",
        score=10,
        completed_steps=["intro"]
    )
    
    assert result.lab_id == "HTTP_01"
    assert result.score == 10
    
    with pytest.raises(Exception):
        result.score = 20  # Frozen Dataclass