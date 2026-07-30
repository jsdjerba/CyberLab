
import random
from typing import Callable, Tuple, Type, Any
from application.ports.delay_provider import DelayProvider
from application.exceptions.application_exceptions import ConcurrencyApplicationException

class RetryPolicy:
    def __init__(
        self,
        delay_provider: DelayProvider,
        retryable_exceptions: Tuple[Type[Exception], ...],
        max_attempts: int = 5,
        initial_delay_ms: int = 50,
        max_delay_ms: int = 500
    ):
        self.delay_provider = delay_provider
        self.retryable_exceptions = retryable_exceptions
        self.max_attempts = max_attempts
        self.initial_delay_ms = initial_delay_ms
        self.max_delay_ms = max_delay_ms

    def execute(self, action: Callable[[], Any]) -> Any:
        attempts_made = 0
        while attempts_made < self.max_attempts:
            attempts_made += 1
            try:
                return action()
            except self.retryable_exceptions as e:
                if attempts_made >= self.max_attempts:
                    raise ConcurrencyApplicationException(f"Max attempts reached: {str(e)}") from e
                
                backoff_ms = min(self.max_delay_ms, self.initial_delay_ms * (2 ** attempts_made))
                delay_ms = random.uniform(0, backoff_ms)
                self.delay_provider.sleep(delay_ms / 1000.0)
