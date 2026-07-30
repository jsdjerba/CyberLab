"""
Tests unitaires et d'intégration TDD pour la couche de persistance SQLAlchemy (Phase 3.2).
Valide les modèles, les mappers, le repository, la préservation des états et l'isolement du domaine.
"""

import sys
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.database import Base
from infrastructure.persistence.models.lab_instance_model import LabInstanceModel, ObjectiveModel, AttemptModel
from infrastructure.persistence.mappers.lab_instance_mapper import LabInstanceMapper
from infrastructure.persistence.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository

from domain.entities.lab_instance import LabInstance
from domain.entities.objective import Objective
from domain.entities.attempt import Attempt
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.attempt_id import AttemptId
from domain.value_objects.correlation_id import CorrelationId
from domain.value_objects.lab_status import LabStatus


@pytest.fixture
def db_session():
    """Fournit une session SQLite en mémoire isolée pour chaque test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


def test_lab_instance_model_creation():
    """Test 1 : Création directe des modèles SQLAlchemy."""
    model = LabInstanceModel(
        id="stu-1#-lab-1",
        student_id="stu-1",
        lab_id="lab-1",
        status=LabStatus.IN_PROGRESS
    )
    assert model.student_id == "stu-1"
    assert model.lab_id == "lab-1"
    assert model.status == LabStatus.IN_PROGRESS


def test_domain_to_database_mapping():
    """Test 2 : Conversion Domain → Database via le Mapper."""
    obj = Objective(objective_id=ObjectiveId("obj-1"), score_weight=20, is_completed=True)
    lab = LabInstance(
        student_id="stu-1",
        lab_id="lab-1",
        objectives=[obj],
        status=LabStatus.COMPLETED
    )

    model = LabInstanceMapper.to_persistence(lab)
    assert model.student_id == "stu-1"
    assert model.lab_id == "lab-1"
    assert model.status == LabStatus.COMPLETED
    assert len(model.objectives) == 1
    assert model.objectives[0].objective_id == "obj-1"
    assert model.objectives[0].is_completed is True


def test_database_to_domain_mapping():
    """Test 3 : Conversion Database → Domain via le Mapper."""
    model = LabInstanceModel(
        id="stu-1#-lab-1",
        student_id="stu-1",
        lab_id="lab-1",
        status=LabStatus.IN_PROGRESS
    )
    obj_model = ObjectiveModel(objective_id="obj-1", score_weight=10, is_completed=False)
    model.objectives.append(obj_model)

    lab = LabInstanceMapper.to_domain(model)
    assert isinstance(lab, LabInstance)
    assert lab.student_id.value == "stu-1"
    assert lab.lab_id.value == "lab-1"
    assert lab.status == LabStatus.IN_PROGRESS
    assert len(lab.objectives) == 1
    assert lab.objectives[0].objective_id.value == "obj-1"


def test_repository_save_and_reload(db_session):
    """Test 4 : Repository save + reload."""
    repo = SqlAlchemyLabInstanceRepository(db_session)
    lab = LabInstance(
        student_id="stu-2",
        lab_id="lab-2",
        status=LabStatus.IN_PROGRESS
    )

    repo.save(lab)
    db_session.commit()

    reloaded = repo.find_by_id("stu-2", "lab-2")
    assert reloaded is not None
    assert reloaded.student_id.value == "stu-2"
    assert reloaded.lab_id.value == "lab-2"
    assert reloaded.status == LabStatus.IN_PROGRESS
    assert repo.exists("stu-2", "lab-2") is True


def test_repository_preserves_completed_objectives(db_session):
    """Test 5 : Préservation des objectifs complétés."""
    repo = SqlAlchemyLabInstanceRepository(db_session)
    obj = Objective(objective_id=ObjectiveId("obj-flag"), score_weight=50, is_completed=True)
    lab = LabInstance(
        student_id="stu-3",
        lab_id="lab-3",
        objectives=[obj],
        status=LabStatus.IN_PROGRESS
    )

    repo.save(lab)
    db_session.commit()

    reloaded = repo.find_by_id("stu-3", "lab-3")
    assert reloaded.objectives[0].is_completed is True
    assert reloaded.objectives[0].score_weight == 50


def test_repository_preserves_attempt_history(db_session):
    """Test 6 : Préservation historique Attempts."""
    repo = SqlAlchemyLabInstanceRepository(db_session)
    lab = LabInstance(student_id="stu-4", lab_id="lab-4")
    
    attempt = Attempt(
        attempt_id=AttemptId("att-99"),
        objective_id=ObjectiveId("obj-1"),
        correlation_id=CorrelationId("corr-123"),
        timestamp=datetime.now(timezone.utc),
        is_correct=False
    )
    object.__setattr__(lab, '_attempts', [attempt])

    repo.save(lab)
    db_session.commit()

    reloaded = repo.find_by_id("stu-4", "lab-4")
    assert len(reloaded.attempts) == 1
    assert reloaded.attempts[0].attempt_id.value == "att-99"
    assert reloaded.attempts[0].correlation_id.value == "corr-123"
    assert reloaded.attempts[0].is_correct is False


def test_domain_has_no_sqlalchemy_dependency():
    """Test 7 : Vérification programmatique que domain/ ne dépend jamais de SQLAlchemy."""
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith("domain."):
            mod = sys.modules[mod_name]
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                assert "sqlalchemy" not in str(type(attr)).lower(), f"Contamination détectée dans le domaine : {attr_name}"