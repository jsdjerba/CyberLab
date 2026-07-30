import pytest
from datetime import datetime, timezone
from typing import Optional

from application.commands.create_classroom_command import CreateClassroomCommand
from application.dto.classroom_response import ClassroomResponseDTO
from application.use_cases.create_classroom import CreateClassroomUseCase
from application.ports.classroom_repository import ClassroomRepository
from application.ports.unit_of_work import UnitOfWork
from application.ports.id_generator import IdGenerator
from application.ports.clock import Clock

from domain.entities.classroom import Classroom
from domain.value_objects.classroom_id import ClassroomId

# --- FAKES TDD OBLIGATOIRES ---

class FakeIdGenerator(IdGenerator):
    def __init__(self):
        self._counter = 0

    def generate(self) -> str:
        self._counter += 1
        return f"classroom-00{self._counter}"

class FakeClock(Clock):
    def now(self) -> datetime:
        return datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

class FakeRepository(ClassroomRepository):
    def __init__(self):
        self.saved_classrooms: list[Classroom] = []
        self._staging: list[Classroom] = []

    def save(self, classroom: Classroom) -> None:
        # Simulation d'un comportement transactionnel (staging avant commit)
        self._staging.append(classroom)

    def find_by_id(self, classroom_id: ClassroomId) -> Optional[Classroom]:
        all_items = self.saved_classrooms + self._staging
        return next((c for c in all_items if c.id == classroom_id), None)

    def commit_staging(self):
        self.saved_classrooms.extend(self._staging)
        self._staging.clear()

    def rollback_staging(self):
        self._staging.clear()

class FakeUnitOfWork(UnitOfWork):
    def __init__(self, repository: FakeRepository, should_fail: bool = False):
        self._repository = repository
        self.commit_called = False
        self.rollback_called = False
        self._should_fail = should_fail

    def begin(self) -> None:
        pass

    def commit(self) -> None:
        if self._should_fail:
            self.rollback()
            raise RuntimeError("Database error during commit")
        self._repository.commit_staging()
        self.commit_called = True

    def rollback(self) -> None:
        self._repository.rollback_staging()
        self.rollback_called = True

    def __enter__(self) -> 'FakeUnitOfWork':
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()


# --- TESTS UNITAIRES ---

def test_create_classroom_success():
    repo = FakeRepository()
    uow = FakeUnitOfWork(repository=repo, should_fail=False)
    id_gen = FakeIdGenerator()
    clock = FakeClock()

    use_case = CreateClassroomUseCase(
        repository=repo,
        unit_of_work=uow,
        id_generator=id_gen,
        clock=clock
    )

    command = CreateClassroomCommand(
        tenant_id="DEFAULT",
        name="CyberSec Lab 101",
        teacher_id="teacher-1",
        max_students=30,
        allow_team_switch=True,
        allow_multiple_teachers=False
    )

    result = use_case.execute(command)

    assert result.classroom_id == "classroom-001"
    assert result.tenant_id == "DEFAULT"
    assert result.name == "CyberSec Lab 101"
    assert result.status == "ACTIVE"
    assert result.primary_teacher_id == "teacher-1"
    
    assert len(repo.saved_classrooms) == 1
    assert repo.saved_classrooms[0].id.value == "classroom-001"
    
    assert uow.commit_called is True
    assert uow.rollback_called is False
    assert type(result) == ClassroomResponseDTO


def test_create_classroom_rollbacks_on_error():
    repo = FakeRepository()
    uow = FakeUnitOfWork(repository=repo, should_fail=True) # Simule une erreur de commit
    id_gen = FakeIdGenerator()
    clock = FakeClock()

    use_case = CreateClassroomUseCase(
        repository=repo,
        unit_of_work=uow,
        id_generator=id_gen,
        clock=clock
    )

    command = CreateClassroomCommand(
        tenant_id="DEFAULT",
        name="CyberSec Lab 101",
        teacher_id="teacher-1"
    )

    with pytest.raises(RuntimeError, match="Database error during commit"):
        use_case.execute(command)

    assert uow.commit_called is False
    assert uow.rollback_called is True
    assert len(repo.saved_classrooms) == 0


def test_create_classroom_does_not_expose_domain_entity():
    repo = FakeRepository()
    uow = FakeUnitOfWork(repository=repo)
    use_case = CreateClassroomUseCase(repo, uow, FakeIdGenerator(), FakeClock())
    
    command = CreateClassroomCommand("DEFAULT", "Test Class", "t-1")
    result = use_case.execute(command)

    assert not isinstance(result, Classroom)
    assert type(result) == ClassroomResponseDTO