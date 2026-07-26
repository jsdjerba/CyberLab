import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database.models.lab import Lab as LabModel
from database.models.progress import Progress as ProgressModel
from infrastructure.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.lab_status import LabStatus
from domain.labs.value_objects.step_id import StepId

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_get_by_id_returns_none_if_absent(db_session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    result = repo.get_by_id("non-existent-id")
    assert result is None

def test_get_by_id_reconstructs_lab_instance(db_session):
    # Arrange : Création d'un Lab ORM et d'un Progress ORM associés
    lab_orm = LabModel(id=1, lab_id="L_SEC_01", title="Network Sec", category="Sec", difficulty="Easy", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    progress_orm = ProgressModel(
        domain_id="inst-abc-123",
        user_id=99,
        lab_id=lab_orm.id,
        status="IN_PROGRESS",
        started_at=datetime(2026, 7, 26, 14, 0, 0),
        completed_at=None
    )
    db_session.add(progress_orm)
    db_session.flush()

    repo = SqlAlchemyLabInstanceRepository(db_session)

    # Act
    instance = repo.get_by_id("inst-abc-123")

    # Assert
    assert instance is not None
    assert instance.id == "inst-abc-123"
    assert isinstance(instance.student_id, StudentId)
    assert isinstance(instance.lab_id, LabId)
    assert instance.lab_id.value == "L_SEC_01"
    assert instance.status == LabStatus.IN_PROGRESS

def test_save_creates_new_progress(db_session):
    lab_orm = LabModel(id=5, lab_id="L_WEB_02", title="Web Hacking", category="Sec", difficulty="Medium", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    repo = SqlAlchemyLabInstanceRepository(db_session)
    instance = LabInstance("inst-new-456", StudentId(10), LabId("L_WEB_02"))
    instance.status = LabStatus.NOT_STARTED

    # Act
    repo.save(instance)

    # Assert
    saved_progress = db_session.query(ProgressModel).filter(ProgressModel.domain_id == "inst-new-456").first()
    assert saved_progress is not None
    assert saved_progress.user_id == 10
    assert saved_progress.lab_id == 5
    assert saved_progress.status == "NOT_STARTED"

def test_save_updates_existing_progress(db_session):
    lab_orm = LabModel(id=2, lab_id="L_CRYPTO_01", title="Crypto", category="Sec", difficulty="Hard", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    progress_orm = ProgressModel(
        domain_id="inst-upd-789",
        user_id=3,
        lab_id=lab_orm.id,
        status="IN_PROGRESS",
        started_at=datetime(2026, 7, 26, 10, 0, 0)
    )
    db_session.add(progress_orm)
    db_session.flush()

    repo = SqlAlchemyLabInstanceRepository(db_session)
    instance = LabInstance("inst-upd-789", StudentId(3), LabId("L_CRYPTO_01"))
    instance.status = LabStatus.COMPLETED
    instance.completed_at = datetime(2026, 7, 26, 12, 0, 0)

    # Act
    repo.save(instance)

    # Assert
    updated_progress = db_session.query(ProgressModel).filter(ProgressModel.domain_id == "inst-upd-789").first()
    assert updated_progress.status == "COMPLETED"
    assert updated_progress.completed_at is not None

def test_mapping_lab_id_business_to_technical_is_correct(db_session):
    lab_orm = LabModel(id=77, lab_id="L_FORENSICS", title="Forensics", category="Sec", difficulty="Hard", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    repo = SqlAlchemyLabInstanceRepository(db_session)
    instance = LabInstance("inst-map-test", StudentId(1), LabId("L_FORENSICS"))
    instance.status = LabStatus.IN_PROGRESS

    # Act
    repo.save(instance)

    # Assert : Le Progress ORM doit lier l'ID technique 77 et non la chaîne "L_FORENSICS"
    progress_orm = db_session.query(ProgressModel).filter(ProgressModel.domain_id == "inst-map-test").first()
    assert progress_orm.lab_id == 77