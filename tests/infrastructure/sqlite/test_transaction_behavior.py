import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from infrastructure.persistence.sqlite.database import create_sqlite_engine
from infrastructure.persistence.sqlite.session import SqlAlchemyUnitOfWork
from infrastructure.persistence.sqlite.models import Base

@pytest.fixture
def file_session_factory(tmp_path):
    # Fichier temporaire pour simuler le comportement réel (Offline First)
    db_path = tmp_path / "test_transaction.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def test_transaction_commit_persists_data(file_session_factory):
    uow = SqlAlchemyUnitOfWork(file_session_factory)
    
    with uow:
        uow.session.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"))
        uow.session.execute(text("INSERT INTO test_table (name) VALUES ('CyberLab')"))
        uow.commit()

    # Vérification dans une nouvelle session / connexion
    with file_session_factory() as session:
        result = session.execute(text("SELECT name FROM test_table")).scalar()
        assert result == 'CyberLab'

def test_transaction_rollback_discards_changes(file_session_factory):
    uow = SqlAlchemyUnitOfWork(file_session_factory)
    
    with file_session_factory() as setup_session:
        setup_session.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"))
        setup_session.commit()

    try:
        with uow:
            uow.session.execute(text("INSERT INTO test_table (name) VALUES ('CyberLab')"))
            raise ValueError("Simulated Domain Exception")
    except ValueError:
        pass

    # Vérification hors transaction : La donnée ne doit pas exister
    with file_session_factory() as session:
        result = session.execute(text("SELECT COUNT(*) FROM test_table")).scalar()
        assert result == 0

def test_session_is_closed_after_context_exit(file_session_factory):
    uow = SqlAlchemyUnitOfWork(file_session_factory)
    
    with uow:
        assert uow.session is not None
        
    # Le UnitOfWork garantit la fermeture et détruit la référence
    assert uow.session is None, "La session SQLAlchemy doit être purgée du UnitOfWork"