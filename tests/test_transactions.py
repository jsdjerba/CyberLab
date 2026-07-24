import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.base import Base
from database.unit_of_work import UnitOfWork
from database.models.user import User
from repositories.sqlalchemy.user_repository import UserRepository

@pytest.fixture
def db_session():
    # Base de données en mémoire pour des tests rapides et isolés
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_rollback_on_exception(db_session):
    repo = UserRepository(db_session)
    
    try:
        with UnitOfWork(db_session) as uow:
            user = User(username="test_rollback", password_hash="hash")
            repo.create(user)
            # On simule une erreur critique dans le service
            raise ValueError("Erreur critique de simulation")
    except ValueError:
        pass  # L'erreur est rattrapée, le rollback a dû être exécuté
    
    # Vérification : L'utilisateur ne doit PAS exister en base
    assert repo.get_by_username("test_rollback") is None

def test_successful_commit(db_session):
    repo = UserRepository(db_session)
    
    with UnitOfWork(db_session) as uow:
        user = User(username="test_commit", password_hash="hash")
        repo.create(user)
        # Succès : pas d'erreur, le commit automatique doit se faire
        
    # Vérification : L'utilisateur DOIT exister en base
    assert repo.get_by_username("test_commit") is not None