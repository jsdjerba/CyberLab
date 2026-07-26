import pytest
from infrastructure.adapters.challenge_validation_adapter import ChallengeValidationAdapter
from application.dtos.validation_result_dto import ValidationResult
from database.models.lab import Lab as LabModel
from database.models.flag import Flag as FlagModel

class FakeQuery:
    def __init__(self, result=None):
        self._result = result
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return self._result

class FakeSession:
    def __init__(self, lab_model=None, flag_model=None):
        self._lab_model = lab_model
        self._flag_model = flag_model
        self._query_count = 0

    def query(self, model):
        self._query_count += 1
        # Premier appel (LabModel), deuxième appel (FlagModel)
        if self._query_count == 1:
            return FakeQuery(self._lab_model)
        return FakeQuery(self._flag_model)

class FakeFlagValidationService:
    def __init__(self, validation_result: bool = True):
        self._validation_result = validation_result

    def validate_flag(self, submitted_flag: str, expected_flag: str, *, case_sensitive: bool = False) -> bool:
        return self._validation_result


def test_challenge_validation_success():
    # Arrange
    lab_orm = LabModel(id=1, lab_id="L1", title="Test Lab", category="Sec", difficulty="Easy", version="1.0", is_active=True)
    flag_orm = FlagModel(id=1, lab_id=1, step_id="step-1", flag_hash="hashed_secret", points=10)
    
    session = FakeSession(lab_model=lab_orm, flag_model=flag_orm)
    service = FakeFlagValidationService(validation_result=True)
    
    adapter = ChallengeValidationAdapter(session=session, flag_validation_service=service)

    # Act
    result = adapter.validate(lab_id="L1", step_id="step-1", submitted_answer="FLAG{secret}")

    # Assert
    assert isinstance(result, ValidationResult)
    assert result.success is True
    assert result.reason is None


def test_challenge_validation_lab_not_found():
    # Arrange
    session = FakeSession(lab_model=None, flag_model=None)
    service = FakeFlagValidationService(validation_result=True)
    
    adapter = ChallengeValidationAdapter(session=session, flag_validation_service=service)

    # Act
    result = adapter.validate(lab_id="UNKNOWN", step_id="step-1", submitted_answer="FLAG{secret}")

    # Assert
    assert result.success is False
    assert result.reason == "Lab not found"


def test_challenge_validation_flag_not_found():
    # Arrange
    lab_orm = LabModel(id=1, lab_id="L1", title="Test Lab", category="Sec", difficulty="Easy", version="1.0", is_active=True)
    session = FakeSession(lab_model=lab_orm, flag_model=None)
    service = FakeFlagValidationService(validation_result=True)
    
    adapter = ChallengeValidationAdapter(session=session, flag_validation_service=service)

    # Act
    result = adapter.validate(lab_id="L1", step_id="step-unknown", submitted_answer="FLAG{secret}")

    # Assert
    assert result.success is False
    assert result.reason == "Flag not found"


def test_challenge_validation_invalid_flag():
    # Arrange
    lab_orm = LabModel(id=1, lab_id="L1", title="Test Lab", category="Sec", difficulty="Easy", version="1.0", is_active=True)
    flag_orm = FlagModel(id=1, lab_id=1, step_id="step-1", flag_hash="hashed_secret", points=10)
    
    session = FakeSession(lab_model=lab_orm, flag_model=flag_orm)
    service = FakeFlagValidationService(validation_result=False)
    
    adapter = ChallengeValidationAdapter(session=session, flag_validation_service=service)

    # Act
    result = adapter.validate(lab_id="L1", step_id="step-1", submitted_answer="WRONG{flag}")

    # Assert
    assert result.success is False
    assert result.reason == "Invalid flag"