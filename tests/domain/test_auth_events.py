from datetime import datetime, timezone
from domain.events.user_registered import UserRegistered
from domain.events.user_logged_in import UserLoggedIn
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.password_hash import PasswordHash
from domain.value_objects.role import Role

def test_user_registered_event_emitted():
    register_time = datetime(2026, 6, 1, tzinfo=timezone.utc)
    user = User.create(
        user_id=UserId("u-event-1"), 
        email=Email("test@test.com"), 
        password_hash=PasswordHash("hashed_string"), 
        role=Role.TEACHER,
        current_time=register_time
    )
    
    events = user.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], UserRegistered)
    assert events[0].user_id == "u-event-1"
    assert events[0].role == "TEACHER"
    assert events[0].timestamp == register_time

def test_user_logged_in_event_emitted():
    user = User.create(
        user_id=UserId("u-event-2"), 
        email=Email("t@t.com"), 
        password_hash=PasswordHash("hashed_string"), 
        role=Role.STUDENT,
        current_time=datetime(2026, 6, 1, tzinfo=timezone.utc)
    )
    user.collect_events() # Purge
    
    login_time = datetime(2026, 6, 2, tzinfo=timezone.utc)
    user.login(current_time=login_time)
    
    events = user.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], UserLoggedIn)
    assert events[0].timestamp == login_time