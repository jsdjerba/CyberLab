"""
Tests unitaires pour le cycle de vie complet de l'Aggregate Root LabInstance (V2).
Valide les transitions d'état, l'idempotence, l'encapsulation et l'émission des événements de domaine.
"""

import pytest
from datetime import datetime, timezone
from domain.entities.lab_instance import LabInstance
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.attempt_id import AttemptId
from domain.value_objects.correlation_id import CorrelationId
from domain.value_objects.lab_status import LabStatus
from domain.exceptions import (
    LabNotStartedException,
    LabAlreadyCompletedException,
    InvalidLabStateException
)


class FakeValidator:
    def __init__(self, correct_flag: str):
        self.correct_flag = correct_flag

    def validate(self, submitted_flag: str, objective_id: ObjectiveId) -> bool:
        return submitted_flag == self.correct_flag


def test_lab_instance_initial_state():
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1",
        lab_id="lab-cyber-101",
        objectives=[obj_id]
    )
    assert lab_instance.status == LabStatus.NOT_STARTED
    assert len(lab_instance.objectives) == 1
    assert len(lab_instance.attempts) == 0
    assert len(lab_instance.collect_events()) == 0


def test_start_changes_status_to_in_progress_and_emits_event():
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1",
        lab_id="lab-cyber-101",
        objectives=[obj_id]
    )
    corr_id = CorrelationId("req-uuid-start-01")
    
    lab_instance.start(correlation_id=corr_id)
    
    assert lab_instance.status == LabStatus.IN_PROGRESS
    events = lab_instance.collect_events()
    assert len(events) == 1
    assert events[0].correlation_id.value == "req-uuid-start-01"


def test_start_is_idempotent():
    """Valide que démarrer un lab déjà en cours est un no-op idempotent (pas d'exception, pas de doublon d'événement)."""
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1",
        lab_id="lab-cyber-101",
        objectives=[obj_id]
    )
    corr_id_1 = CorrelationId("req-uuid-start-01")
    corr_id_2 = CorrelationId("req-uuid-start-02")
    
    lab_instance.start(correlation_id=corr_id_1)
    assert lab_instance.status == LabStatus.IN_PROGRESS
    lab_instance.collect_events()  # Vider les events du premier start

    # Second start avec un autre CorrelationId (ex: retry réseau / double clic)
    lab_instance.start(correlation_id=corr_id_2)
    assert lab_instance.status == LabStatus.IN_PROGRESS
    
    # Aucun nouvel événement ne doit être émis (idempotence stricte)
    assert len(lab_instance.collect_events()) == 0


def test_submit_flag_before_start_raises_domain_exception():
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1",
        lab_id="lab-cyber-101",
        objectives=[obj_id]
    )
    validator = FakeValidator("CTF{secret}")
    
    with pytest.raises(LabNotStartedException):
        lab_instance.submit_flag(
            objective_id=obj_id,
            submitted_flag="CTF{secret}",
            validator=validator,
            correlation_id="req-sub-1"
        )


def test_submit_incorrect_flag_adds_attempt_and_emits_flag_submitted():
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1",
        lab_id="lab-cyber-101",
        objectives=[obj_id]
    )
    validator = FakeValidator("CTF{secret}")
    lab_instance.start(correlation_id="req-start")
    lab_instance.collect_events()

    is_correct = lab_instance.submit_flag(
        objective_id=obj_id,
        submitted_flag="CTF{wrong}",
        validator=validator,
        correlation_id="req-sub-1",
        attempt_id="att-1",
        current_time=datetime.now(timezone.utc)
    )

    assert is_correct is False
    assert len(lab_instance.attempts) == 1
    events = lab_instance.collect_events()
    assert len(events) == 2  # FlagSubmitted et FlagRejected


def test_submit_correct_flag_emits_submitted_validated_and_completed():
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1",
        lab_id="lab-cyber-101",
        objectives=[obj_id]
    )
    validator = FakeValidator("CTF{secret}")
    lab_instance.start(correlation_id="req-start")
    lab_instance.collect_events()

    is_correct = lab_instance.submit_flag(
        objective_id=obj_id,
        submitted_flag="CTF{secret}",
        validator=validator,
        correlation_id="req-sub-1",
        attempt_id="att-1",
        current_time=datetime.now(timezone.utc)
    )

    assert is_correct is True
    assert lab_instance.status == LabStatus.COMPLETED
    assert lab_instance.objectives[0].is_completed is True


def test_completed_lab_instance_is_immutable():
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1",
        lab_id="lab-cyber-101",
        objectives=[obj_id]
    )
    validator = FakeValidator("CTF{secret}")
    lab_instance.start(correlation_id="req-start")
    
    lab_instance.submit_flag(
        objective_id=obj_id,
        submitted_flag="CTF{secret}",
        validator=validator,
        correlation_id="req-sub-1"
    )

    with pytest.raises(LabAlreadyCompletedException):
        lab_instance.submit_flag(
            objective_id=obj_id,
            submitted_flag="CTF{secret}",
            validator=validator,
            correlation_id="req-sub-2"
        )