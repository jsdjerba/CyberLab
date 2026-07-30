
from typing import Sequence, Any
from application.ports.unit_of_work import UnitOfWork

class FakeUnitOfWork(UnitOfWork):
    def __init__(self):
        self.commit_called = False
        self.rollback_called = False
        self._events = []
        self._should_fail_on_commit = False
        self._fail_exception = None

    def simulate_failure(self, exception: Exception):
        self._should_fail_on_commit = True
        self._fail_exception = exception

    def begin(self) -> None:
        pass

    def commit(self) -> None:
        if self._should_fail_on_commit:
            self._should_fail_on_commit = False # succeed on next try
            self.rollback()
            raise self._fail_exception
        self.commit_called = True

    def rollback(self) -> None:
        self.rollback_called = True

    def register_events(self, events: Sequence[Any]) -> None:
        self._events.extend(events)

    def collect_events(self) -> Sequence[Any]:
        collected = list(self._events)
        self._events.clear()
        return collected

    def __enter__(self) -> 'FakeUnitOfWork':
        self.begin()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type:
            self.rollback()
