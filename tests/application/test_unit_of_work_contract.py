"""
Tests de contrat pour le port UnitOfWork.
"""

import pytest
from application.ports.unit_of_work import UnitOfWork


class DummyUoW:
    """Implémentation factice (Dummy) pour tester le contrat UoW."""
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.committed = True
        self.rolled_back = False

    def rollback(self):
        self.rolled_back = True
        self.committed = False


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