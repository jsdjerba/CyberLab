"""Politique de réessai (Retry Pattern) pour les erreurs techniques transitoires (SQLite database locked)."""
from typing import Callable, Type, Tuple
from application.exceptions.classroom_application_exceptions import DatabaseLockedException

class RetryPolicy:
    def __init__(self, max_attempts: int = 3, exceptions_to_retry: Tuple[Type[Exception], ...] = (DatabaseLockedException,)):
        self.max_attempts = max_attempts
        self._exceptions_to_retry = exceptions_to_retry
        self.execution_count = 0

    def execute(self, action: Callable[[], any]) -> any:
        self.execution_count = 0
        attempt = 0
        while attempt < self.max_attempts:
            attempt += 1
            self.execution_count = attempt
            try:
                return action()
            except self._exceptions_to_retry:
                if attempt >= self.max_attempts:
                    raise
                # En production, un léger backoff pourrait être appliqué ici.