import pytest
import tempfile
import os
from sqlalchemy import text, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from infrastructure.persistence.database_setup import create_resilient_sqlite_engine

@pytest.fixture
def temp_sqlite_db():
    """Fournit un fichier SQLite temporaire pour tester le mode WAL."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    yield f"sqlite:///{path}"
    
    # Cleanup : suppression du fichier principal et des fichiers WAL/SHM résiduels
    for ext in ["", "-wal", "-shm"]:
        file_path = path + ext
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                pass  # Tolérance aux verrous persistants de l'OS après fermeture

def test_sqlite_engine_enforces_resilience_pragmas(temp_sqlite_db):
    """
    Vérifie que chaque nouvelle connexion SQLite générée par notre Engine
    active obligatoirement le mode WAL, le busy_timeout et les Foreign Keys.
    """
    engine = create_resilient_sqlite_engine(temp_sqlite_db)
    try:
        with engine.connect() as conn:
            journal_mode = conn.execute(text("PRAGMA journal_mode;")).scalar()
            assert journal_mode.lower() == "wal", "Le mode WAL n'est pas activé."
            
            busy_timeout = conn.execute(text("PRAGMA busy_timeout;")).scalar()
            assert str(busy_timeout) == "5000", "Le busy_timeout doit être configuré à 5000ms."
            
            foreign_keys = conn.execute(text("PRAGMA foreign_keys;")).scalar()
            assert str(foreign_keys) == "1", "Les Foreign Keys doivent être activées."
    finally:
        engine.dispose()  # Libère explicitement les verrous de fichiers (vital sous Windows)

def test_sqlite_configuration_isolated_per_connection(temp_sqlite_db):
    """
    Vérifie que les PRAGMAs sont appliqués indépendamment sur chaque nouvelle connexion.
    """
    engine = create_resilient_sqlite_engine(temp_sqlite_db)
    try:
        with engine.connect() as conn1:
            fk1 = conn1.execute(text("PRAGMA foreign_keys;")).scalar()
            assert str(fk1) == "1"
            
        with engine.connect() as conn2:
            fk2 = conn2.execute(text("PRAGMA foreign_keys;")).scalar()
            assert str(fk2) == "1"
    finally:
        engine.dispose()

Base = declarative_base()
class DummyModel(Base):
    __tablename__ = 'dummy_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)

def test_sqlite_engine_supports_existing_models(temp_sqlite_db):
    """
    Vérifie que notre configuration résiliente ne casse pas les opérations CRUD SQLAlchemy.
    """
    engine = create_resilient_sqlite_engine(temp_sqlite_db)
    try:
        Base.metadata.create_all(engine)
        
        with Session(engine) as session:
            session.add(DummyModel(name="CyberLab Hardening Test"))
            session.commit()
            
            saved = session.query(DummyModel).first()
            assert saved is not None
            assert saved.name == "CyberLab Hardening Test"
    finally:
        engine.dispose()