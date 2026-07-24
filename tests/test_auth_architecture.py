import inspect
from application.services import auth_service

def test_auth_service_clean_architecture():
    source = inspect.getsource(auth_service.AuthService)
    assert "sqlalchemy" not in source.lower()
    assert "database.models" not in source.lower()

    params = inspect.signature(auth_service.AuthService.__init__).parameters
    assert 'user_repo' in params
    assert 'hasher' in params