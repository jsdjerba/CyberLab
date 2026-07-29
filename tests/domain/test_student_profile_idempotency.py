import pytest
from domain.entities.student_profile import StudentProfile
from domain.events.score_updated import ScoreUpdated

def test_student_profile_adds_score_and_generates_event_first_time():
    # Arrange
    profile = StudentProfile(student_id="student-123", total_score=0)
    correlation_id = "req-uuid-001"
    
    # Act
    profile.add_score_for_lab(lab_id="lab-x", score=50, correlation_id=correlation_id)
    
    # Assert - Vérification de l'état
    assert profile.total_score == 50
    
    # Assert - Vérification de l'événement généré
    events = profile.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], ScoreUpdated)
    assert events[0].student_id == "student-123"
    assert events[0].added_points == 50
    assert events[0].new_total_score == 50
    assert events[0].correlation_id == correlation_id

def test_student_profile_ignores_duplicate_lab_scoring():
    # Arrange
    profile = StudentProfile(student_id="student-123", total_score=0)
    
    # Premier scoring (accepté)
    profile.add_score_for_lab(lab_id="lab-x", score=50, correlation_id="req-uuid-001")
    profile.collect_events()  # Purge des événements
    
    # Act - Tentative de scoring en double pour le MÊME lab avec un nouveau contexte HTTP
    profile.add_score_for_lab(lab_id="lab-x", score=20, correlation_id="req-uuid-002")
    
    # Assert - Le score doit rester bloqué à 50 (ignorer les 20 points)
    assert profile.total_score == 50
    
    # Assert - Aucun événement ne doit être généré (idempotence)
    events = profile.collect_events()
    assert len(events) == 0

def test_student_profile_accepts_different_labs():
    # Arrange
    profile = StudentProfile(student_id="student-123", total_score=0)
    
    # Act - Scoring pour deux labs distincts
    profile.add_score_for_lab(lab_id="lab-x", score=50, correlation_id="req-uuid-001")
    profile.add_score_for_lab(lab_id="lab-y", score=30, correlation_id="req-uuid-002")
    
    # Assert
    assert profile.total_score == 80
    events = profile.collect_events()
    assert len(events) == 2

def test_student_profile_rejects_negative_score():
    profile = StudentProfile(student_id="student-123", total_score=0)
    
    # Vérifie l'invariant : total_score >= 0
    with pytest.raises(ValueError, match="Le score total ne peut pas être négatif"):
        # Si on tente de retirer plus de points que le score total disponible
        profile.add_score_for_lab(lab_id="lab-x", score=-10, correlation_id="req-1")