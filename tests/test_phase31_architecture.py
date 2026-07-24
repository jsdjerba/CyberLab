import application.services.auth_service as auth
import core.security.password_hasher as hasher
import database.seeds.runner as seeds
import inspect

def test_auth_service_purity():
    source = inspect.getsource(auth)
    assert "sqlalchemy" not in source.lower()
    assert "database.models" not in source.lower()

def test_hasher_purity():
    source = inspect.getsource(hasher)
    assert "argon2" in source.lower()
    assert "hashlib" not in source.lower()