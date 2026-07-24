from application.common.interfaces.unit_of_work import UnitOfWork
from infrastructure.fakes.fake_lab_repository import FakeLabRepository
from infrastructure.fakes.fake_lab_instance_repository import FakeLabInstanceRepository

class FakeUnitOfWork(UnitOfWork):
    def __init__(self):
        self.labs = FakeLabRepository()
        self.lab_instances = FakeLabInstanceRepository()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True