import pytest
from dataclasses import FrozenInstanceError

from domain.labs.services.achievement_service import AchievementService
from domain.labs.entities.lab import Lab
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.entities.step import Step
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.step_type import StepType
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.student_history import StudentHistory
from domain.labs.value_objects.badge_id import BadgeId
from domain.labs.value_objects.achievement import Achievement

@pytest.fixture
def achievement_service():
    return AchievementService()

@pytest.fixture
def sample_lab():
    return Lab(
        id=LabId("LAB_ACH_01"),
        title="Security Basics",
        description="Test Lab",
        difficulty="BEGINNER",
        duration=30, # minutes
        steps=[Step(StepId("s1"), StepType.FLAG, "F1", 50)]
    )

@pytest.fixture
def sample_instance(sample_lab):
    instance = LabInstance(
        id="INST_01",
        lab_id=sample_lab.id,
        student_id=StudentId(1)
    )
    instance.is_finished = True
    instance.score = 50
    instance.duration_seconds = 600 # 10 minutes (rapide pour 30 min estimées)
    return instance

def test_value_objects_immutability():
    badge = BadgeId("TEST")
    ach = Achievement(badge, "Title", "Desc")
    history = StudentHistory(1, ("L1",), 2)

    with pytest.raises(FrozenInstanceError):
        badge.value = "NEW" # type: ignore
    with pytest.raises(FrozenInstanceError):
        ach.title = "New Title" # type: ignore
    with pytest.raises(FrozenInstanceError):
        history.current_streak = 5 # type: ignore

def test_unfinished_instance_returns_no_achievements(achievement_service, sample_lab, sample_instance):
    sample_instance.is_finished = False
    history = StudentHistory(completed_lab_count=0, successful_lab_ids=())
    
    achievements = achievement_service.evaluate_achievements(sample_instance, sample_lab, history)
    assert achievements == ()

def test_first_blood_achievement(achievement_service, sample_lab, sample_instance):
    history = StudentHistory(completed_lab_count=0, successful_lab_ids=())
    
    achievements = achievement_service.evaluate_achievements(sample_instance, sample_lab, history)
    badge_ids = {a.badge_id.value for a in achievements}
    
    assert "FIRST_BLOOD" in badge_ids

def test_no_first_blood_if_already_completed(achievement_service, sample_lab, sample_instance):
    history = StudentHistory(completed_lab_count=1, successful_lab_ids=(str(sample_lab.id),))
    
    achievements = achievement_service.evaluate_achievements(sample_instance, sample_lab, history)
    badge_ids = {a.badge_id.value for a in achievements}
    
    assert "FIRST_BLOOD" not in badge_ids

def test_perfect_score_achievement(achievement_service, sample_lab, sample_instance):
    sample_instance.score = 50 # Égal au total_points() du lab
    history = StudentHistory(completed_lab_count=1, successful_lab_ids=(str(sample_lab.id),))
    
    achievements = achievement_service.evaluate_achievements(sample_instance, sample_lab, history)
    badge_ids = {a.badge_id.value for a in achievements}
    
    assert "PERFECT_SCORE" in badge_ids

def test_speed_run_achievement(achievement_service, sample_lab, sample_instance):
    sample_instance.duration_seconds = 300 # 5 min pour 30 min estimées (très rapide)
    history = StudentHistory(completed_lab_count=1, successful_lab_ids=(str(sample_lab.id),))
    
    achievements = achievement_service.evaluate_achievements(sample_instance, sample_lab, history)
    badge_ids = {a.badge_id.value for a in achievements}
    
    assert "SPEED_RUN" in badge_ids

def test_milestone_achievement(achievement_service, sample_lab, sample_instance):
    history = StudentHistory(completed_lab_count=4, successful_lab_ids=("L1", "L2", "L3", "L4")) # 4 + 1 = 5 labs
    
    achievements = achievement_service.evaluate_achievements(sample_instance, sample_lab, history)
    badge_ids = {a.badge_id.value for a in achievements}
    
    assert "MILESTONE_5_LABS" in badge_ids

def test_streak_achievement(achievement_service, sample_lab, sample_instance):
    history = StudentHistory(completed_lab_count=5, successful_lab_ids=("L1", "L2"), current_streak=2) # 2 + 1 = 3 streak
    
    achievements = achievement_service.evaluate_achievements(sample_instance, sample_lab, history)
    badge_ids = {a.badge_id.value for a in achievements}
    
    assert "STREAK_3" in badge_ids

def test_service_is_stateless_and_has_no_side_effects(achievement_service, sample_lab, sample_instance):
    history = StudentHistory(completed_lab_count=0, successful_lab_ids=())
    orig_score = sample_instance.score
    orig_finished = sample_instance.is_finished

    achievement_service.evaluate_achievements(sample_instance, sample_lab, history)
    
    assert sample_instance.score == orig_score
    assert sample_instance.is_finished == orig_finished