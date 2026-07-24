
import pytest
from datetime import datetime, timezone

from domain.progress.entities.progress import Progress
from domain.progress.value_objects.progress_status import ProgressStatus
from domain.progress.events.lab_completed_event import LabCompletedEvent
from domain.exceptions import InvalidProgressTransitionError, LabAlreadyCompletedError


def test_create_progress_sets_started_status():
    p = Progress.start(student_id="s1", lab_id="lab1")
    assert p.status == ProgressStatus.STARTED
    assert p.student_id == "s1"
    assert p.lab_id == "lab1"
    assert p.completed_at is None


def test_transition_started_to_completed():
    p = Progress.start(student_id="s1", lab_id="lab1")
    now = datetime.now(timezone.utc)
    p.complete(now=now)
    assert p.status == ProgressStatus.COMPLETED
    assert p.completed_at == now


def test_double_completion_is_forbidden():
    p = Progress.start(student_id="s1", lab_id="lab1")
    p.complete()
    with pytest.raises(LabAlreadyCompletedError):
        p.complete()


def test_cannot_revert_completed_to_started():
    p = Progress.start(student_id="s1", lab_id="lab1")
    p.complete()
    assert not p.status.can_transition_to(ProgressStatus.STARTED)


def test_completion_generates_domain_event():
    p = Progress.start(student_id="s1", lab_id="lab1")
    p.complete()
    events = p.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], LabCompletedEvent)
    assert events[0].student_id == "s1"
    assert events[0].lab_id == "lab1"


def test_pull_events_clears_pending_events():
    p = Progress.start(student_id="s1", lab_id="lab1")
    p.complete()
    p.pull_events()
    assert p.pull_events() == []


def test_student_id_and_lab_id_required():
    with pytest.raises(ValueError):
        Progress.start(student_id="", lab_id="lab1")
    with pytest.raises(ValueError):
        Progress.start(student_id="s1", lab_id="")
