import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.lab_status import LabStatus
from infrastructure.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository

def test_get_by_id_returns_none_if_no_progress():
    session_mock = MagicMock()
    session_mock.query().filter().first.return_value = None
    
    repo = SqlAlchemyLabInstanceRepository(session_mock)
    result = repo.get_by_id("missing_id")
    
    assert result is None

def test_save_raises_value_error_if_lab_not_found():
    session_mock = MagicMock()
    session_mock.query().filter().first.return_value = None
    repo = SqlAlchemyLabInstanceRepository(session_mock)
    
    instance = LabInstance("instance_1", StudentId(1), LabId("LAB_1"))
    instance.status = LabStatus.IN_PROGRESS
    
    with pytest.raises(ValueError, match="Lab with business id 'LAB_1' not found in database."):
        repo.save(instance)

def test_save_adds_new_progress_when_not_existing():
    lab_model_mock = Mock(id=1, lab_id="LAB_1")
    
    session_mock = MagicMock()
    # first call is for LabModel, second is for ProgressModel
    session_mock.query().filter().first.side_effect = [lab_model_mock, None]
    
    repo = SqlAlchemyLabInstanceRepository(session_mock)
    
    instance = LabInstance("instance_1", StudentId(1), LabId("LAB_1"))
    instance.status = LabStatus.IN_PROGRESS
    
    repo.save(instance)
    
    session_mock.add.assert_called_once()
    session_mock.flush.assert_called_once()