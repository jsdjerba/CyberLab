import pytest
from datetime import datetime, timezone
from application.use_cases.register_user import RegisterUserUseCase
from application.dto.auth_dto import RegisterUserCommand
from domain.exceptions.auth_exceptions import DuplicateUserException
from domain.value_objects.password_hash import PasswordHash


# --- Implémentations Fakes pour tests TDD ---
class FakeUserRepository:
    def __init__(self):
        self._users = {}
    
    def save(self, user):
        self._users[user.email.value] = user
        
    def exists(self, email: str) -> bool:
        return email in self._users
        
    def find_by_email(self, email: str):
        return self._users.get(email)
        
    def find_by_id(self, user_id: str):
        for user in self._users.values():
            if user.user_id.value == user_id:
                return user
        return None


class DummyPasswordHasher:
    def hash(self, plaintext: str) -> PasswordHash:
        return PasswordHash(f"dummy_hashed_{plaintext}_extremely_long_string_for_validation")
    
    def verify(self, plaintext: str, hashed: PasswordHash) -> bool:
        return hashed.value == f"dummy_hashed_{plaintext}_extremely_long_string_for_validation"


class FakeIdGenerator:
    def __init__(self, fixed_id: str = "u-fixed-id-123456"):
        self.fixed_id = fixed_id

    def generate(self) -> str:
        return self.fixed_id


# --- Tests ---

def test_register_user_success():
    repo = FakeUserRepository()
    hasher = DummyPasswordHasher()
    id_gen = FakeIdGenerator("u-deterministic-001")
    use_case = RegisterUserUseCase(repo, hasher, id_gen)
    
    cmd = RegisterUserCommand(
        email="new_student@cyberlab.edu",
        password="secure_password",
        role="STUDENT",
        current_time=datetime(2026, 8, 1, tzinfo=timezone.utc)
    )
    
    result = use_case.execute(cmd)
    
    assert result.email == "new_student@cyberlab.edu"
    assert result.role == "STUDENT"
    assert result.user_id == "u-deterministic-001"
    
    saved_user = repo.find_by_email("new_student@cyberlab.edu")
    assert saved_user is not None
    assert saved_user.password_hash.value.startswith("dummy_hashed_secure_password")
    
    events = saved_user.collect_events()
    assert len(events) == 1
    assert events[0].__class__.__name__ == "UserRegistered"


def test_register_duplicate_email_raises_exception():
    repo = FakeUserRepository()
    hasher = DummyPasswordHasher()
    id_gen = FakeIdGenerator()
    use_case = RegisterUserUseCase(repo, hasher, id_gen)
    
    cmd = RegisterUserCommand(
        email="duplicate@cyberlab.edu",
        password="pwd",
        role="STUDENT",
        current_time=datetime(2026, 8, 1, tzinfo=timezone.utc)
    )
    
    use_case.execute(cmd)  # Premier appel
    
    with pytest.raises(DuplicateUserException):
        use_case.execute(cmd)  # Second appel rejeté