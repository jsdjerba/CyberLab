import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.base import Base
from database.unit_of_work import UnitOfWork
from application.services.auth_service import AuthService
from infrastructure.mappers.user_mapper import UserMapper
from domain.enums.user_role import UserRole

class TestUnitOfWorkFactory:
    def __init__(self, session):
        self.session = session
    def create(self):
        return UnitOfWork(self.session)

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_auth_full_flow(db_session):
    uow_factory = TestUnitOfWorkFactory(db_session)
    service = AuthService(uow_factory, UserMapper)
    
    # 1. Register
    user = service.register_user("admin_test", "SecurePassword123", UserRole.ADMIN)
    assert user.username == "admin_test"
    
    # 2. Check Hash
    from database.models import User
    user_db = db_session.query(User).filter_by(username="admin_test").first()
    assert user_db.password_hash.startswith("$argon2id$")
    
    # 3. Authenticate
    assert service.authenticate("admin_test", "SecurePassword123") is not None