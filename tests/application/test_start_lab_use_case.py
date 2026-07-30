"""
Tests unitaires TDD pour StartLabUseCase.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.database import Base
from infrastructure.persistence.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from application.use_cases.start_lab import StartLabUseCase, StartLabCommand
from domain.value_objects.lab_status import LabStatus


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


def test_start_lab_creates_new_instance_and_saves(db_session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    use_case = StartLabUseCase(repo)

    command = StartLabCommand(
        student_id="student-101",
        lab_id="cyber-lab-1",
        correlation_id="corr-start-001"
    )

    result = use_case.execute(command)

    assert result.student_id == "student-101"
    assert result.lab_id == "cyber-lab-1"
    assert result.status == LabStatus.IN_PROGRESS.name
    assert result.correlation_id == "corr-start-001"

    # Vérification de la persistance effective
    reloaded = repo.find_by_id("student-101", "cyber-lab-1")
    assert reloaded is not None
    assert reloaded.status == LabStatus.IN_PROGRESS


def test_start_lab_idempotency(db_session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    use_case = StartLabUseCase(repo)

    cmd1 = StartLabCommand(student_id="student-101", lab_id="cyber-lab-1", correlation_id="corr-1")
    use_case.execute(cmd1)

    # Second démarrage (ex: retry réseau)
    cmd2 = StartLabCommand(student_id="student-101", lab_id="cyber-lab-1", correlation_id="corr-2")
    result = use_case.execute(cmd2)

    assert result.status == LabStatus.IN_PROGRESS
    assert repo.exists("student-101", "cyber-lab-1") is True