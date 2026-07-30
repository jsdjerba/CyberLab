import pytest
from datetime import datetime, timezone
from typing import Optional

from application.commands.enroll_student_command import EnrollStudentCommand
from application.dto.enrollment_response import EnrollmentResponseDTO
from application.exceptions.classroom_application_exceptions import (
    ClassroomNotFoundApplicationException, DatabaseLockedException
)
from application.use_cases.enroll_student import EnrollStudentUseCase
from application.ports.classroom_repository import ClassroomRepository
from application.ports.unit_of_work import UnitOfWork
from application.ports.clock import Clock
from application.policies.retry_policy import RetryPolicy

from domain.entities.classroom import Classroom
from domain.value_objects.tenant_id import TenantId
from domain.value_objects.classroom_id import ClassroomId
from domain.value_objects.classroom_name import ClassroomName
from domain.value_objects.classroom_settings import ClassroomSettings
from domain.value_objects.teacher_id import TeacherId
from domain.value_objects.student_id import StudentId
from domain.value_objects.invitation_code import InvitationCode
from domain.exceptions.classroom_exceptions import InvalidInvitationException

# --- FAKES LOCAUX TDD ---

class FakeRepository(ClassroomRepository):
    def __init__(self, initial_classroom: Optional[Classroom] = None):
        self.saved_classroom: Optional[Classroom] = initial_classroom
        self.find_calls = 0

    def save(self, classroom: Classroom) -> None:
        self.saved_classroom = classroom

    def find_by_id(self, classroom_id: ClassroomId) -> Optional[Classroom]:
        self.find_calls += 1
        if self.saved_classroom and self.saved_classroom.id == classroom_id:
            return self.saved_classroom
        return None

class FakeUnitOfWork(UnitOfWork):
    def __init__(self, fail_count: int = 0, fail_with_exception = DatabaseLockedException):
        self.commit_called = False
        self.rollback_called = False
        self._fail_count = fail_count
        self._fail_exception = fail_with_exception
        self.current_attempts = 0

    def begin(self) -> None:
        pass

    def commit(self) -> None:
        self.current_attempts += 1
        if self.current_attempts <= self._fail_count:
            self.rollback()
            raise self._fail_exception("Database is locked")
        self.commit_called = True

    def rollback(self) -> None:
        self.rollback_called = True

    def __enter__(self) -> 'FakeUnitOfWork':
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()

class FakeClock(Clock):
    def now(self) -> datetime:
        return datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

class FakeRetryPolicy(RetryPolicy):
    def __init__(self, max_attempts: int = 3):
        super().__init__(max_attempts=max_attempts)
        self.attempts_made = 0

    def execute(self, action):
        self.attempts_made = 0
        while self.attempts_made < self.max_attempts:
            self.attempts_made += 1
            try:
                return action()
            except DatabaseLockedException:
                if self.attempts_made >= self.max_attempts:
                    raise


# --- FIXTURE UTILITAIRE ---

@pytest.fixture
def setup_classroom_with_invitation():
    classroom_id = ClassroomId("c-1")
    classroom = Classroom.create(
        tenant_id=TenantId("DEFAULT"),
        classroom_id=classroom_id,
        name=ClassroomName("Cybersec 101"),
        primary_teacher=TeacherId("t-1"),
        settings=ClassroomSettings(max_students=40),
        current_time=datetime(2026, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
        event_id_1="evt-1",
        event_id_2="evt-2"
    )
    code = InvitationCode("SECURE22")
    classroom.generate_invitation(code, datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc), datetime(2026, 1, 1, 11, 0, 0, tzinfo=timezone.utc), "evt-3")
    return classroom


# --- TESTS UNITAIRES ---

def test_student_enrollment_success(setup_classroom_with_invitation):
    classroom = setup_classroom_with_invitation
    repo = FakeRepository(initial_classroom=classroom)
    uow = FakeUnitOfWork(fail_count=0)
    clock = FakeClock()
    retry_policy = FakeRetryPolicy()

    use_case = EnrollStudentUseCase(
        repository=repo,
        unit_of_work=uow,
        clock=clock,
        retry_policy=retry_policy
    )

    command = EnrollStudentCommand(
        classroom_id="c-1",
        student_id="student-99",
        invitation_code="SECURE22"
    )

    result = use_case.execute(command)

    assert repo.find_calls == 1
    assert repo.saved_classroom is not None
    assert StudentId("student-99") in repo.saved_classroom.members
    assert uow.commit_called is True
    assert isinstance(result, EnrollmentResponseDTO)
    assert result.student_id == "student-99"
    assert result.classroom_id == "c-1"


def test_missing_classroom_raises_application_exception():
    repo = FakeRepository(initial_classroom=None)
    uow = FakeUnitOfWork()
    use_case = EnrollStudentUseCase(repo, uow, FakeClock(), FakeRetryPolicy())

    command = EnrollStudentCommand(
        classroom_id="unknown-c",
        student_id="student-99",
        invitation_code="SECURE22"
    )

    with pytest.raises(ClassroomNotFoundApplicationException):
        use_case.execute(command)

    assert repo.find_calls == 1
    assert uow.commit_called is False


def test_invalid_invitation_is_not_retried(setup_classroom_with_invitation):
    classroom = setup_classroom_with_invitation
    repo = FakeRepository(initial_classroom=classroom)
    uow = FakeUnitOfWork()
    retry_policy = FakeRetryPolicy()

    use_case = EnrollStudentUseCase(repo, uow, FakeClock(), retry_policy)

    command = EnrollStudentCommand(
        classroom_id="c-1",
        student_id="student-99",
        invitation_code="BADXYZ7"
    )

    with pytest.raises(InvalidInvitationException):
        use_case.execute(command)

    assert retry_policy.attempts_made == 0 
    assert uow.commit_called is False


def test_database_locked_retries_then_success(setup_classroom_with_invitation):
    classroom = setup_classroom_with_invitation
    repo = FakeRepository(initial_classroom=classroom)
    uow = FakeUnitOfWork(fail_count=1, fail_with_exception=DatabaseLockedException)
    retry_policy = FakeRetryPolicy(max_attempts=3)

    use_case = EnrollStudentUseCase(repo, uow, FakeClock(), retry_policy)

    command = EnrollStudentCommand(
        classroom_id="c-1",
        student_id="student-99",
        invitation_code="SECURE22"
    )

    result = use_case.execute(command)

    assert retry_policy.attempts_made == 2
    assert uow.commit_called is True
    assert StudentId("student-99") in repo.saved_classroom.members
    assert isinstance(result, EnrollmentResponseDTO)


def test_repository_failure_rollbacks(setup_classroom_with_invitation):
    classroom = setup_classroom_with_invitation
    repo = FakeRepository(initial_classroom=classroom)
    uow = FakeUnitOfWork(fail_count=1, fail_with_exception=RuntimeError)
    retry_policy = FakeRetryPolicy(max_attempts=1)

    use_case = EnrollStudentUseCase(repo, uow, FakeClock(), retry_policy)

    command = EnrollStudentCommand(
        classroom_id="c-1",
        student_id="student-99",
        invitation_code="SECURE22"
    )

    with pytest.raises(RuntimeError):
        use_case.execute(command)

    assert uow.rollback_called is True