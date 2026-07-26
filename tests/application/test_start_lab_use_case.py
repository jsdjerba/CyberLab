import pytest
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.lab_status import LabStatus
from domain.exceptions import LabNotFoundError, StudentNotFoundError
from application.commands.start_lab_command import StartLabCommand
from application.use_cases.start_lab_use_case import StartLabUseCase

# --- Dummies & Fakes conformes aux invariants du Domain ---

class DummyStep:
    def __init__(self, step_id=StepId("s1")):
        self.id = step_id

class DummyLab:
    def __init__(self, lab_id=LabId("L1"), steps=None):
        self.id = lab_id
        # Respect de l'invariant LabInstance.start_lab : un lab ne doit pas être vide
        self.steps = steps if steps is not None else [DummyStep()]

class FakeLabRepo:
    def __init__(self, lab=None):
        self._lab = lab
    def get_by_id(self, lab_id):
        if self._lab and self._lab.id == lab_id:
            return self._lab
        return None

class FakeStudentRepo:
    def __init__(self, exists=True):
        self._exists = exists
    def get_history(self, student_id):
        return object() if self._exists else None

class FakeInstanceRepo:
    def __init__(self):
        self.saved_instances = {}
    def save(self, instance):
        self.saved_instances[instance.id] = instance
    def get_by_id(self, instance_id):
        return self.saved_instances.get(instance_id)

class FakeEventBus:
    def __init__(self):
        self.published_events = []
    def publish(self, events):
        self.published_events.extend(events)

# --- Tests ---

def test_start_lab_success():
    lab_id = LabId("L1")
    student_id = StudentId(1)
    lab = DummyLab(lab_id=lab_id)

    lab_repo = FakeLabRepo(lab)
    student_repo = FakeStudentRepo(exists=True)
    instance_repo = FakeInstanceRepo()
    event_bus = FakeEventBus()

    use_case = StartLabUseCase(
        lab_repository=lab_repo,
        lab_instance_repository=instance_repo,
        student_repository=student_repo,
        event_bus=event_bus,
        id_generator=lambda: "inst_uuid_123"
    )

    command = StartLabCommand(student_id=student_id, lab_id=lab_id)
    instance_id = use_case.execute(command)

    assert instance_id == "inst_uuid_123"
    
    saved_instance = instance_repo.get_by_id("inst_uuid_123")
    assert saved_instance is not None
    assert saved_instance.status == LabStatus.IN_PROGRESS
    assert len(event_bus.published_events) > 0

def test_start_lab_raises_lab_not_found():
    lab_repo = FakeLabRepo(lab=None)
    student_repo = FakeStudentRepo(exists=True)
    instance_repo = FakeInstanceRepo()
    event_bus = FakeEventBus()

    use_case = StartLabUseCase(
        lab_repository=lab_repo,
        lab_instance_repository=instance_repo,
        student_repository=student_repo,
        event_bus=event_bus
    )

    command = StartLabCommand(student_id=StudentId(1), lab_id=LabId("UNKNOWN"))
    with pytest.raises(LabNotFoundError):
        use_case.execute(command)

def test_start_lab_raises_student_not_found():
    lab_id = LabId("L1")
    lab = DummyLab(lab_id=lab_id)

    lab_repo = FakeLabRepo(lab)
    student_repo = FakeStudentRepo(exists=False)
    instance_repo = FakeInstanceRepo()
    event_bus = FakeEventBus()

    use_case = StartLabUseCase(
        lab_repository=lab_repo,
        lab_instance_repository=instance_repo,
        student_repository=student_repo,
        event_bus=event_bus
    )

    command = StartLabCommand(student_id=StudentId(999), lab_id=lab_id)
    with pytest.raises(StudentNotFoundError):
        use_case.execute(command)