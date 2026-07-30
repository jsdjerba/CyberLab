import pytest
from datetime import datetime, timezone
from application.use_cases.login_user import LoginUserUseCase
from application.dto.auth_dto import LoginUserCommand
from domain.exceptions.auth_exceptions import UserNotFoundException, InvalidPasswordException, AuthenticationError
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.password_hash import PasswordHash
from domain.value_objects.role import Role


# --- Fakes ---
class FakeUserRepository:
    def __init__(self):
        self._users = {}

    def save(self, user):
        self._users[user.email.value] = user

    def find_by_email(self, email: str):
        return self._users.get(email)

    def exists(self, email: str) -> bool:
        return email in self._users

    def find_by_id(self, user_id: str):
        for user in self._users.values():
            if user.user_id.value == user_id:
                return user
        return None


class DummyPasswordHasher:
    def hash(self, plaintext: str) -> PasswordHash:
        return PasswordHash(f"dummy_hash_{plaintext}_long")

    def verify(self, plaintext: str, hashed: PasswordHash) -> bool:
        return hashed.value == f"dummy_hash_{plaintext}_long"


class DummyTokenProvider:
    def create_token(self, user_id: str, role: str) -> str:
        return f"fake_jwt_for_{user_id}_{role}"


# --- Fixtures & Tests ---
@pytest.fixture
def populated_repo():
    repo = FakeUserRepository()
    user = User.register(
        user_id=UserId("u-login-1"),
        email=Email("teacher@cyberlab.edu"),
        password_hash=PasswordHash("dummy_hash_correct_pwd_long"),
        role=Role.TEACHER,
        current_time=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )
    user.collect_events()  # Purge des événements initiaux
    repo.save(user)
    return repo


def test_login_success(populated_repo):
    hasher = DummyPasswordHasher()
    token_provider = DummyTokenProvider()
    use_case = LoginUserUseCase(populated_repo, hasher, token_provider)
    
    login_time = datetime(2026, 9, 1, tzinfo=timezone.utc)
    cmd = LoginUserCommand(
        email="teacher@cyberlab.edu",
        password="correct_pwd",
        current_time=login_time
    )
    
    result = use_case.execute(cmd)
    
    assert result.user_id == "u-login-1"
    assert result.role == "TEACHER"
    assert result.token == "fake_jwt_for_u-login-1_TEACHER"
    
    user_state = populated_repo.find_by_email("teacher@cyberlab.edu")
    events = user_state.collect_events()
    assert len(events) == 1
    assert events[0].__class__.__name__ == "UserLoggedIn"
    assert events[0].timestamp == login_time


def test_login_invalid_password_raises_exception(populated_repo):
    use_case = LoginUserUseCase(populated_repo, DummyPasswordHasher(), DummyTokenProvider())
    
    cmd = LoginUserCommand("teacher@cyberlab.edu", "wrong_pwd", datetime(2026, 9, 1, tzinfo=timezone.utc))
    
    with pytest.raises(InvalidPasswordException):
        use_case.execute(cmd)


def test_login_non_existent_user_raises_exception(populated_repo):
    use_case = LoginUserUseCase(populated_repo, DummyPasswordHasher(), DummyTokenProvider())
    
    cmd = LoginUserCommand("nobody@cyberlab.edu", "correct_pwd", datetime(2026, 9, 1, tzinfo=timezone.utc))
    
    with pytest.raises(UserNotFoundException):
        use_case.execute(cmd)


def test_login_deactivated_user_raises_exception(populated_repo):
    user = populated_repo.find_by_email("teacher@cyberlab.edu")
    user.deactivate()
    populated_repo.save(user)
    
    use_case = LoginUserUseCase(populated_repo, DummyPasswordHasher(), DummyTokenProvider())
    cmd = LoginUserCommand("teacher@cyberlab.edu", "correct_pwd", datetime(2026, 9, 1, tzinfo=timezone.utc))
    
    with pytest.raises(AuthenticationError, match="désactivé"):
        use_case.execute(cmd)