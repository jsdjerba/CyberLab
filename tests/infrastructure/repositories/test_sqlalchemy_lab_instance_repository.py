import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from infrastructure.database.base import Base
from infrastructure.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.lab_status import LabStatus

@pytest.fixture
def db_session():
    # SQLite in-memory pour isoler les tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_save_and_reconstruct_aggregate(db_session: Session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    student = StudentId(42)
    lab = LabId("HTTP_LAB")
    
    # 1. Création état domaine avancé
    instance = LabInstance("inst_uuid_123", student, lab)
    instance.status = LabStatus.IN_PROGRESS
    instance.current_step = StepId("flag_2")
    instance.score = 150
    instance.completed_steps = [StepId("flag_1")]
    instance.attempts = {"flag_1": 1, "flag_2": 4}
    
    # 2. Persistance SQLAlchemy
    repo.save(instance)
    db_session.commit()
    
    # 3. Récupération
    retrieved = repo.get_by_student_and_lab(student, lab)
    
    # 4. Assertions strictes (Reconstruction parfaite)
    assert retrieved is not None
    assert retrieved.id == "inst_uuid_123"
    assert retrieved.status == LabStatus.IN_PROGRESS
    assert retrieved.current_step.value == "flag_2"
    assert retrieved.score == 150
    assert len(retrieved.completed_steps) == 1
    assert retrieved.completed_steps[0].value == "flag_1"
    assert retrieved.attempts == {"flag_1": 1, "flag_2": 4}

def test_get_missing_returns_none(db_session: Session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    assert repo.get_by_student_and_lab(StudentId(99), LabId("UNKNOWN")) is None

def test_student_isolation(db_session: Session):
    repo = SqlAlchemyLabInstanceRepository(db_session)
    
    inst1 = LabInstance("inst_A", StudentId(1), LabId("LAB_1"))
    inst2 = LabInstance("inst_B", StudentId(2), LabId("LAB_1"))
    
    repo.save(inst1)
    repo.save(inst2)
    db_session.commit()
    
    res1 = repo.get_by_student_and_lab(StudentId(1), LabId("LAB_1"))
    res2 = repo.get_by_student_and_lab(StudentId(2), LabId("LAB_1"))
    
    assert res1.id == "inst_A"
    assert res2.id == "inst_B"