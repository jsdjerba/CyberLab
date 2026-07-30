import pytest
from datetime import datetime, timezone
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.password_hash import PasswordHash
from domain.value_objects.role import Role
from domain.exceptions.auth_exceptions import AuthenticationError

@pytest.fixture
def valid_user_params():
    return {
        "user_id": UserId("u-1"),
        "email": Email("admin@cyberlab.edu"),
        "password_hash": PasswordHash("some_hashed_string"),
        "role": Role.ADMIN,
        "current_time": datetime(2026, 1, 1, tzinfo=timezone.utc)
    }

def test_register_creates_active_user_and_events(valid_user_params):
    user = User.create(**valid_user_params)
    
    assert user.user_id.value == "u-1"
    assert user.email.value == "admin@cyberlab.edu"
    assert user.role == Role.ADMIN
    assert user.is_active is True
    
    events = user.collect_events()
    assert len(events) == 1
    assert events[0].user_id == "u-1"
    assert events[0].timestamp == datetime(2026, 1, 1, tzinfo=timezone.utc)
    
    # Vérification que le collect a vidé la liste (Pattern read-and-clear)
    assert len(user.collect_events()) == 0
    
def test_deactivate_and_activate_user(valid_user_params):
    user = User.create(**valid_user_params)
    user.collect_events() # purge
    
    user.deactivate()
    assert user.is_active is False
    
    user.activate()
    assert user.is_active is True

def test_login_success(valid_user_params):
    user = User.create(**valid_user_params)
    user.collect_events() # Purge init event
    
    login_time = datetime(2026, 2, 1, tzinfo=timezone.utc)
    user.login(current_time=login_time)
    
    events = user.collect_events()
    assert len(events) == 1
    assert events[0].timestamp == login_time

def test_login_deactivated_user_raises_exception(valid_user_params):
    user = User.create(**valid_user_params)
    user.deactivate()
    
    with pytest.raises(AuthenticationError, match="compte utilisateur est désactivé"):
        user.login(current_time=datetime(2026, 2, 1, tzinfo=timezone.utc))