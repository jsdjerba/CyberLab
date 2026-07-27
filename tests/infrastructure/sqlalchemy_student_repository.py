import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database.models.user import User as UserModel
from database.models.progress import Progress as ProgressModel
from database.models.lab import Lab as LabModel
from infrastructure.repositories.sqlalchemy_student_repository import SqlAlchemyStudentRepository
from domain.students.value_objects.student_history import StudentHistory
from domain.labs.value_objects.student_id import StudentId

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_get_history_user_absent_returns_none(db_session):
    repo = SqlAlchemyStudentRepository(db_session)
    result = repo.get_history(StudentId(999))
    assert result is None

def test_get_history_user_without_completed_labs(db_session):
    user_orm = UserModel(
        id=1,
        domain_id="student_domain_1",
        username="alice",
        password_hash="hash",
        role="STUDENT",
        xp=0,
        created_at=datetime.utcnow()
    )
    db_session.add(user_orm)
    db_session.flush()

    repo = SqlAlchemyStudentRepository(db_session)
    history = repo.get_history(StudentId(1))

    assert isinstance(history, StudentHistory)
    assert history.completed_lab_count == 0
    assert history.successful_lab_ids == ()
    assert history.current_streak == 0

def test_get_history_user_with_multiple_completed_labs(db_session):
    user_orm = UserModel(
        id=2,
        domain_id="student_domain_2",
        username="bob",
        password_hash="hash",
        role="STUDENT",
        xp=100,
        created_at=datetime.utcnow()
    )
    lab1 = LabModel(id=10, lab_id="L_SEC_01", title="Sec 1", category="Sec", difficulty="Easy", version="1.0", is_active=True)
    lab2 = LabModel(id=20, lab_id="L_WEB_01", title="Web 1", category="Sec", difficulty="Med", version="1.0", is_active=True)
    
    db_session.add_all([user_orm, lab1, lab2])
    db_session.flush()

    prog1 = ProgressModel(domain_id="p1", user_id=2, lab_id=10, status="COMPLETED", started_at=datetime.utcnow(), completed_at=datetime.utcnow())
    prog2 = ProgressModel(domain_id="p2", user_id=2, lab_id=20, status="COMPLETED", started_at=datetime.utcnow(), completed_at=datetime.utcnow())
    
    db_session.add_all([prog1, prog2])
    db_session.flush()

    repo = SqlAlchemyStudentRepository(db_session)
    history = repo.get_history(StudentId(2))

    assert history.completed_lab_count == 2
    assert set(history.successful_lab_ids) == {"L_SEC_01", "L_WEB_01"}
    assert isinstance(history.successful_lab_ids, tuple)

def test_student_id_value_mapping(db_session):
    # Vérifie que le repository cible précisément l'ID technique User.id via StudentId.value
    user_target = UserModel(id=42, domain_id="target", username="charlie", password_hash="h", role="STUDENT", xp=50, created_at=datetime.utcnow())
    user_other = UserModel(id=43, domain_id="other", username="david", password_hash="h", role="STUDENT", xp=50, created_at=datetime.utcnow())
    
    lab = LabModel(id=5, lab_id="L_CRYPTO", title="Crypto", category="Sec", difficulty="Hard", version="1.0", is_active=True)
    db_session.add_all([user_target, user_other, lab])
    db_session.flush()

    prog = ProgressModel(domain_id="ptarget", user_id=42, lab_id=5, status="COMPLETED", started_at=datetime.utcnow(), completed_at=datetime.utcnow())
    db_session.add(prog)
    db_session.flush()

    repo = SqlAlchemyStudentRepository(db_session)
    history = repo.get_history(StudentId(42))

    assert history.completed_lab_count == 1
    assert history.successful_lab_ids == ("L_CRYPTO",)

def test_no_orm_leakage(db_session):
    # Vérifie que le type retourné est strictement un objet Domaine (StudentHistory) et non un modèle ORM
    user_orm = UserModel(id=1, domain_id="d1", username="eve", password_hash="h", role="STUDENT", xp=0, created_at=datetime.utcnow())
    db_session.add(user_orm)
    db_session.flush()

    repo = SqlAlchemyStudentRepository(db_session)
    history = repo.get_history(StudentId(1))

    assert not isinstance(history, UserModel)
    assert not isinstance(history, ProgressModel)
    assert type(history).__name__ == "StudentHistory"