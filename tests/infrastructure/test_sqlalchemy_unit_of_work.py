import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.base import Base
from infrastructure.persistence.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork

@pytest.fixture
def sqlite_session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    return session_maker

def test_sqlalchemy_uow_commit(sqlite_session_factory):
    uow = SqlAlchemyUnitOfWork(sqlite_session_factory)
    with uow:
        # Vérifie que la session est initialisée et que les repositories sont attachés
        assert uow.session is not None
        assert uow.labs is not None
        uow.commit()

def test_sqlalchemy_uow_rollback_on_exception(sqlite_session_factory):
    uow = SqlAlchemyUnitOfWork(sqlite_session_factory)
    with pytest.raises(RuntimeError):
        with uow:
            raise RuntimeError("Force rollback")