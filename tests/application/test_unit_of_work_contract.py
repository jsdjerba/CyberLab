import pytest
from application.ports.unit_of_work import AbstractUnitOfWork

class DummyUoW(AbstractUnitOfWork):
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def collect_events(self) -> list:
        return []

def test_uow_context_manager_success():
    uow = DummyUoW()
    with uow:
        pass
    assert uow.committed is True
    assert uow.rolled_back is False

def test_uow_context_manager_exception():
    uow = DummyUoW()
    with pytest.raises(ValueError):
        with uow:
            raise ValueError("Erreur métier test")
    assert uow.committed is False
    assert uow.rolled_back is True