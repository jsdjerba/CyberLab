import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from database.base import Base

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    # ... (le reste de ton code de configuration SQLite)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()