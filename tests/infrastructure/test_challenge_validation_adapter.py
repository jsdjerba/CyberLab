import pytest
from unittest.mock import Mock
from application.dtos.validation_result_dto import ValidationResult
from infrastructure.adapters.challenge_validation_adapter import ChallengeValidationAdapter
from database.models.lab import Lab as LabModel
from database.models.flag import Flag as FlagModel

class MockQuery:
    def __init__(self, result=None):
        self._result = result
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return self._result

class MockSession:
    def __init__(self, lab_model=None, flag_model=None):
        self._lab_model = lab_model
        self._flag_model = flag_model

    def query(self, model):
        if model == LabModel:
            return MockQuery(self._lab_model)
        elif model == FlagModel:
            return MockQuery(self._flag_model)
        return MockQuery(None)

def test_validate_lab_not_found():
    session = MockSession(lab_model=None)
    adapter = ChallengeValidationAdapter(session, Mock())
    result = adapter.validate("LAB1", "STEP1", "flag")
    assert result.success is False
    assert result.reason == "Lab not found"

def test_validate_flag_not_found():
    lab = LabModel(id=1, lab_id="LAB1")
    session = MockSession(lab_model=lab, flag_model=None)
    adapter = ChallengeValidationAdapter(session, Mock())
    result = adapter.validate("LAB1", "STEP1", "flag")
    assert result.success is False
    assert result.reason == "Flag not found"

def test_validate_invalid_flag():
    lab = LabModel(id=1, lab_id="LAB1")
    flag = FlagModel(id=1, lab_id=1, step_id="STEP1", flag_hash="hash")
    session = MockSession(lab_model=lab, flag_model=flag)
    flag_service = Mock()
    flag_service.validate_flag.return_value = False
    
    adapter = ChallengeValidationAdapter(session, flag_service)
    result = adapter.validate("LAB1", "STEP1", "wrong_flag")
    
    assert result.success is False
    assert result.reason == "Invalid flag"

def test_validate_success():
    lab = LabModel(id=1, lab_id="LAB1")
    flag = FlagModel(id=1, lab_id=1, step_id="STEP1", flag_hash="hash")
    session = MockSession(lab_model=lab, flag_model=flag)
    flag_service = Mock()
    flag_service.validate_flag.return_value = True
    
    adapter = ChallengeValidationAdapter(session, flag_service)
    result = adapter.validate("LAB1", "STEP1", "correct_flag")
    
    assert result.success is True