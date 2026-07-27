import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.lab_status import LabStatus
from infrastructure.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository

from database.models.lab import Lab as LabModel
from database.models.progress import Progress as ProgressModel
from database.models.user import User as UserModel

@pytest.fixture
def db_session():
    """
    Fixture locale créant une base de données SQLite en mémoire
    et instanciant une session SQLAlchemy propre pour chaque test.
    """
    engine = create_engine("sqlite:///:memory:")
    # Création de toutes les tables basées sur les modèles déclaratifs
    UserModel.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_get_missing_returns_none(db_session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    assert repo.get_by_id("missing_id") is None


def test_get_by_id_reconstructs_lab_instance(db_session):
    # 1. Création de l'utilisateur avec password_hash pour satisfaire la contrainte NOT NULL
    user_orm = UserModel(id=99, username="test_user_99", password_hash="dummy_hash")
    db_session.add(user_orm)

    # 2. Création du Lab
    lab_orm = LabModel(id=1, lab_id="L_SEC_01", title="Network Sec", category="Sec", difficulty="Easy", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    # 3. Création du Progress
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

    # 4. Act & Assert
    repo = SqlAlchemyLabInstanceRepository(db_session)
    instance = repo.get_by_id("inst-abc-123")
    
    assert instance is not None
    assert instance.id == "inst-abc-123"
    assert instance.student_id.value == 99
    assert instance.lab_id.value == "L_SEC_01"
    assert instance.status == LabStatus.IN_PROGRESS


def test_save_creates_new_progress(db_session):
    # 1. Création de l'utilisateur avec password_hash pour la FK
    user_orm = UserModel(id=10, username="test_user_10", password_hash="dummy_hash")
    db_session.add(user_orm)

    # 2. Création du Lab
    lab_orm = LabModel(id=5, lab_id="L_WEB_02", title="Web Hacking", category="Sec", difficulty="Medium", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    # 3. Act
    repo = SqlAlchemyLabInstanceRepository(db_session)
    instance = LabInstance("inst-new-456", StudentId(10), LabId("L_WEB_02"))
    instance.status = LabStatus.NOT_STARTED
    repo.save(instance)

    # 4. Assert
    saved = db_session.query(ProgressModel).filter_by(domain_id="inst-new-456").first()
    assert saved is not None
    assert saved.user_id == 10
    assert saved.lab_id == 5


def test_save_updates_existing_progress(db_session):
    # 1. Création de l'utilisateur avec password_hash pour la FK
    user_orm = UserModel(id=3, username="test_user_3", password_hash="dummy_hash")
    db_session.add(user_orm)

    # 2. Création du Lab
    lab_orm = LabModel(id=2, lab_id="L_CRYPTO_01", title="Crypto", category="Sec", difficulty="Hard", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    # 3. Création du Progress initial
    progress_orm = ProgressModel(
        domain_id="inst-upd-789",
        user_id=3,
        lab_id=lab_orm.id,
        status="IN_PROGRESS",
        started_at=datetime(2026, 7, 26, 10, 0, 0)
    )
    db_session.add(progress_orm)
    db_session.flush()

    # 4. Act (Mise à jour)
    repo = SqlAlchemyLabInstanceRepository(db_session)
    instance = repo.get_by_id("inst-upd-789")
    instance.status = LabStatus.COMPLETED
    instance.completed_at = datetime(2026, 7, 26, 11, 0, 0)
    repo.save(instance)

    # 5. Assert
    updated = db_session.query(ProgressModel).filter_by(domain_id="inst-upd-789").first()
    status_str = updated.status.value if hasattr(updated.status, 'value') else updated.status
    assert status_str == "COMPLETED"


def test_mapping_lab_id_business_to_technical_is_correct(db_session):
    # 1. Création de l'utilisateur avec password_hash pour la FK
    user_orm = UserModel(id=1, username="test_user_1", password_hash="dummy_hash")
    db_session.add(user_orm)

    # 2. Création du Lab
    lab_orm = LabModel(id=77, lab_id="L_FORENSICS", title="Forensics", category="Sec", difficulty="Hard", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    # 3. Act
    repo = SqlAlchemyLabInstanceRepository(db_session)
    instance = LabInstance("inst-map-test", StudentId(1), LabId("L_FORENSICS"))
    instance.status = LabStatus.IN_PROGRESS
    repo.save(instance)

    # 4. Assert
    saved = db_session.query(ProgressModel).filter_by(domain_id="inst-map-test").first()
    assert saved.lab_id == 77


def test_save_and_reconstruct_aggregate(db_session):
    # 1. Création de l'utilisateur avec password_hash pour la FK
    user_orm = UserModel(id=42, username="test_user_42", password_hash="dummy_hash")
    db_session.add(user_orm)

    # 2. Création du Lab
    lab_orm = LabModel(id=10, lab_id="HTTP_LAB", title="HTTP Lab", category="Sec", difficulty="Easy", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    # 3. Act (Sauvegarde)
    repo = SqlAlchemyLabInstanceRepository(db_session)
    student = StudentId(42)
    lab = LabId("HTTP_LAB")
    instance = LabInstance("inst_uuid_123", student, lab)
    instance.status = LabStatus.IN_PROGRESS
    repo.save(instance)

    # 4. Act (Reconstruction)
    reconstructed = repo.get_by_id("inst_uuid_123")
    
    # 5. Assert
    assert reconstructed.id == "inst_uuid_123"
    assert reconstructed.student_id == student
    assert reconstructed.lab_id == lab
    assert reconstructed.status == LabStatus.IN_PROGRESS


def test_student_isolation(db_session):
    # 1. Création de deux utilisateurs distincts avec password_hash
    user_orm_1 = UserModel(id=1, username="student_1", password_hash="dummy_hash")
    user_orm_2 = UserModel(id=2, username="student_2", password_hash="dummy_hash")
    db_session.add_all([user_orm_1, user_orm_2])

    # 2. Création du Lab
    lab_orm = LabModel(id=1, lab_id="LAB_1", title="Lab 1", category="Sec", difficulty="Easy", version="1.0", is_active=True)
    db_session.add(lab_orm)
    db_session.flush()

    # 3. Act
    repo = SqlAlchemyLabInstanceRepository(db_session)

    inst1 = LabInstance("inst_A", StudentId(1), LabId("LAB_1"))
    inst1.status = LabStatus.NOT_STARTED
    inst2 = LabInstance("inst_B", StudentId(2), LabId("LAB_1"))
    inst2.status = LabStatus.NOT_STARTED

    repo.save(inst1)
    repo.save(inst2)

    # 4. Assert
    fetched1 = repo.get_by_student_and_lab(StudentId(1), LabId("LAB_1"))
    fetched2 = repo.get_by_student_and_lab(StudentId(2), LabId("LAB_1"))

    assert fetched1.id == "inst_A"
    assert fetched2.id == "inst_B"