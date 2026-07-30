"""
Tests unitaires TDD pour SubmitFlagUseCase.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.database import Base
from infrastructure.persistence.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from application.use_cases.start_lab import StartLabUseCase, StartLabCommand
from application.use_cases.submit_flag import SubmitFlagUseCase, SubmitFlagCommand
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.lab_status import LabStatus
from domain.exceptions import LabInstanceNotFoundError, LabAlreadyCompletedException


class DummyValidator:
    def validate(self, flag: str, objective_id: ObjectiveId) -> bool:
        return flag == "CTF{correct_flag}"


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


def test_submit_correct_flag_completes_lab(db_session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    obj_id = ObjectiveId("obj-1")

    # 1. Démarrer le lab d'abord
    start_uc = StartLabUseCase(repo)
    start_uc.execute(StartLabCommand(
        student_id="student-202",
        lab_id="cyber-lab-2",
        correlation_id="corr-start",
        objectives=[obj_id]
    ))

    # 2. Soumettre le bon flag via le use case
    submit_uc = SubmitFlagUseCase(repo, DummyValidator())
    result = submit_uc.execute(SubmitFlagCommand(
        student_id="student-202",
        lab_id="cyber-lab-2",
        objective_id="obj-1",
        submitted_flag="CTF{correct_flag}",
        correlation_id="corr-sub-1",
        current_time=datetime.now(timezone.utc)
    ))

    assert result.is_correct is True
    assert result.status == LabStatus.COMPLETED.name
    assert result.objective_id == "obj-1"


def test_submit_flag_on_non_existent_lab_raises_exception(db_session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    submit_uc = SubmitFlagUseCase(repo, DummyValidator())

    with pytest.raises(LabInstanceNotFoundError):
        submit_uc.execute(SubmitFlagCommand(
            student_id="ghost-student",
            lab_id="ghost-lab",
            objective_id="obj-1",
            submitted_flag="CTF{wrong}",
            correlation_id="corr-1"
        ))


def test_submit_flag_on_completed_lab_raises_exception(db_session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    obj_id = ObjectiveId("obj-1")

    start_uc = StartLabUseCase(repo)
    start_uc.execute(StartLabCommand(
        student_id="student-303",
        lab_id="cyber-lab-3",
        correlation_id="corr-start",
        objectives=[obj_id]
    ))

    submit_uc = SubmitFlagUseCase(repo, DummyValidator())
    
    # Première soumission réussie
    submit_uc.execute(SubmitFlagCommand(
        student_id="student-303",
        lab_id="cyber-lab-3",
        objective_id="obj-1",
        submitted_flag="CTF{correct_flag}",
        correlation_id="corr-sub-1"
    ))

    # Deuxième soumission sur lab déjà complété doit lever une exception
    with pytest.raises(LabAlreadyCompletedException):
        submit_uc.execute(SubmitFlagCommand(
            student_id="student-303",
            lab_id="cyber-lab-3",
            objective_id="obj-1",
            submitted_flag="CTF{correct_flag}",
            correlation_id="corr-sub-2"
        ))