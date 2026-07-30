
import pytest
from datetime import datetime
from application.resilience.retry_policy import RetryPolicy
from application.exceptions.application_exceptions import ConcurrencyApplicationException

from tests.fakes.fake_clock import FakeClock
from tests.fakes.fake_id_generator import FakeIdGenerator
from tests.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.fakes.fake_event_publisher import FakeEventPublisher
from tests.fakes.fake_delay_provider import FakeDelayProvider

class DatabaseLockedException(Exception):
    pass
class BusinessException(Exception):
    pass

# --- PORTS / FAKES TESTS ---

def test_fake_clock_returns_fixed_time():
    dt = datetime(2026, 7, 30, 12, 0, 0)
    clock = FakeClock(dt)
    assert clock.now() == dt

def test_fake_id_generator_returns_sequential_ids():
    gen = FakeIdGenerator()
    assert gen.generate() == "id-1"
    assert gen.generate() == "id-2"
    assert gen.generate() == "id-3"

def test_fake_uow_commit_success():
    uow = FakeUnitOfWork()
    uow.commit()
    assert uow.commit_called is True
    assert uow.rollback_called is False

def test_fake_uow_rollbacks_on_exception():
    uow = FakeUnitOfWork()
    uow.simulate_failure(RuntimeError("error"))
    with pytest.raises(RuntimeError):
        uow.commit()
    assert uow.commit_called is False
    assert uow.rollback_called is True

def test_fake_uow_collects_events():
    uow = FakeUnitOfWork()
    uow.register_events(["evt-1", "evt-2"])
    events = uow.collect_events()
    assert events == ["evt-1", "evt-2"]
    assert uow.collect_events() == [] # emptied

def test_fake_event_publisher_stores_events():
    pub = FakeEventPublisher()
    pub.publish(["evt-1", "evt-2"])
    assert pub.published_events == ["evt-1", "evt-2"]


# --- RETRY POLICY TESTS ---

def test_retry_policy_succeeds_after_temporary_failure():
    delay_provider = FakeDelayProvider()
    policy = RetryPolicy(delay_provider, retryable_exceptions=(DatabaseLockedException,))
    
    attempts = 0
    def action():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise DatabaseLockedException("locked")
        return "success"
        
    result = policy.execute(action)
    
    assert result == "success"
    assert attempts == 2
    assert len(delay_provider.sleep_calls) == 1

def test_retry_policy_stops_after_max_attempts():
    delay_provider = FakeDelayProvider()
    policy = RetryPolicy(delay_provider, retryable_exceptions=(DatabaseLockedException,), max_attempts=3)
    
    def action():
        raise DatabaseLockedException("locked")
        
    with pytest.raises(ConcurrencyApplicationException, match="Max attempts reached"):
        policy.execute(action)
        
    assert len(delay_provider.sleep_calls) == 2 # delay after 1st and 2nd attempt. 3rd fails and raises.

def test_retry_policy_uses_exponential_backoff():
    delay_provider = FakeDelayProvider()
    policy = RetryPolicy(delay_provider, retryable_exceptions=(DatabaseLockedException,), max_attempts=4, initial_delay_ms=50, max_delay_ms=500)
    
    def action():
        raise DatabaseLockedException("locked")
        
    with pytest.raises(ConcurrencyApplicationException):
        policy.execute(action)
        
    assert len(delay_provider.sleep_calls) == 3
    
    # 1st attempt fails -> backoff max 100ms
    assert delay_provider.sleep_calls[0] <= 100.0 / 1000.0
    # 2nd attempt fails -> backoff max 200ms
    assert delay_provider.sleep_calls[1] <= 200.0 / 1000.0
    # 3rd attempt fails -> backoff max 400ms
    assert delay_provider.sleep_calls[2] <= 400.0 / 1000.0

def test_retry_policy_uses_jitter():
    # Run multiple times to ensure delays are not uniform fixed steps
    delay_provider = FakeDelayProvider()
    policy = RetryPolicy(delay_provider, retryable_exceptions=(DatabaseLockedException,), max_attempts=2, initial_delay_ms=500)
    
    delays = []
    for _ in range(10):
        def action():
            raise DatabaseLockedException("locked")
        try:
            policy.execute(action)
        except ConcurrencyApplicationException:
            pass
        delays.append(delay_provider.sleep_calls[-1])
        
    # Check that they are not all identical (probability of that is practically zero with uniform(0, backoff))
    unique_delays = set(delays)
    assert len(unique_delays) > 1

def test_retry_policy_does_not_retry_business_exception():
    delay_provider = FakeDelayProvider()
    policy = RetryPolicy(delay_provider, retryable_exceptions=(DatabaseLockedException,))
    
    def action():
        raise BusinessException("Business error")
        
    with pytest.raises(BusinessException):
        policy.execute(action)
        
    assert len(delay_provider.sleep_calls) == 0
