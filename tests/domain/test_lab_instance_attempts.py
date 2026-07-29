"""
Tests unitaires pour l'historique et la sécurité des tentatives (Attempts) dans LabInstance V2.
"""

import pytest
from datetime import datetime, timezone
from domain.entities.lab_instance import LabInstance
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.correlation_id import CorrelationId


class FakeFlagValidationService:
    def __init__(self, correct_flag: str):
        self.correct_flag = correct_flag

    def validate(self, submitted_flag: str, objective_id: ObjectiveId) -> bool:
        return submitted_flag == self.correct_flag


def test_attempts_chronological_history_and_incremental_numbers():
    # Arrange : On associe explicitement un objective_id valide à l'agrégat
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1", 
        lab_id="lab-101",
        objectives=[obj_id]
    )
    validator = FakeFlagValidationService("CTF{win}")
    lab_instance.start(correlation_id=CorrelationId("req-1"))

    # Tentative 1 (Échouée) - Passage explicite de l'objective_id en premier argument
    lab_instance.submit_flag(
        objective_id=obj_id,
        submitted_flag="CTF{bad1}",
        validator=validator,
        correlation_id=CorrelationId("req-2")
    )

    # Tentative 2 (Échouée)
    lab_instance.submit_flag(
        objective_id=obj_id,
        submitted_flag="CTF{bad2}",
        validator=validator,
        correlation_id=CorrelationId("req-3")
    )

    # Tentative 3 (Réussie)
    lab_instance.submit_flag(
        objective_id=obj_id,
        submitted_flag="CTF{win}",
        validator=validator,
        correlation_id=CorrelationId("req-4")
    )

    attempts = lab_instance.attempts
    assert len(attempts) == 3
    assert attempts[0].is_correct is False
    assert attempts[1].is_correct is False
    assert attempts[2].is_correct is True


def test_attempt_does_not_store_plaintext_flag_insecurely():
    """Vérifie que l'entité Attempt ne stocke pas le flag soumis en clair (sécurité)."""
    obj_id = ObjectiveId("obj-1")
    lab_instance = LabInstance(
        student_id="student-1", 
        lab_id="lab-101",
        objectives=[obj_id]
    )
    validator = FakeFlagValidationService("CTF{secret}")
    lab_instance.start(correlation_id=CorrelationId("req-1"))

    sensitive_flag = "CTF{super_secret_password_123}"
    lab_instance.submit_flag(
        objective_id=obj_id,
        submitted_flag=sensitive_flag,
        validator=validator,
        correlation_id=CorrelationId("req-2")
    )

    attempts = lab_instance.attempts
    assert len(attempts) == 1
    
    # Vérification qu'aucun attribut ne stocke le flag en clair sur l'objet Attempt
    attempt = attempts[0]
    assert not hasattr(attempt, "submitted_flag")
    assert not hasattr(attempt, "flag")
    assert "CTF{super_secret_password_123}" not in repr(attempt)