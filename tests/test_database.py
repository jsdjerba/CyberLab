import pytest
import tempfile
import os
from sqlalchemy import text, Column, Integer, String
from sqlalchemy.orm import declarative_base
from database.session import get_engine, get_session_factory

Base = declarative_base()

class DummyTestModel(Base):
    __tablename__ = 'dummy_test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)

@pytest.fixture
def file_engine():
    """Crée une base SQLite sur fichier physique pour pouvoir tester le WAL."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    engine = get_engine(f"sqlite:///{path}")
    Base.metadata.create_all(engine)
    
    yield engine
    
    engine.dispose()
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def file_session_factory(file_engine):
    return get_session_factory(file_engine)


def test_foreign_keys_enabled(file_engine):
    with file_engine.connect() as conn:
        res = conn.execute(text("PRAGMA foreign_keys;")).scalar()
        assert res == 1

def test_wal_enabled(file_engine):
    with file_engine.connect() as conn:
        res = conn.execute(text("PRAGMA journal_mode;")).scalar()
        # En mode fichier, on s'attend strictement à 'wal'
        assert res.lower() == "wal"

def test_synchronous_mode(file_engine):
    with file_engine.connect() as conn:
        res = conn.execute(text("PRAGMA synchronous;")).scalar()
        # 1 correspond à NORMAL sous SQLite
        assert res == 1

def test_database_rollback_with_wal(file_session_factory):
    # Vérifie l'intégrité transactionnelle
    with file_session_factory() as session:
        session.add(DummyTestModel(name="test_rollback"))
        session.flush()
        session.rollback()
    
    with file_session_factory() as session:
        count = session.query(DummyTestModel).filter_by(name="test_rollback").count()
        assert count == 0