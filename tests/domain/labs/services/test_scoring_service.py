import pytest
from domain.labs.value_objects.scoring_context import ScoringContext
from domain.labs.policies.scoring_policy import ScoringPolicy
from domain.labs.services.scoring_service import ScoringService
from domain.labs.exceptions import InvalidScoreContext

@pytest.fixture
def scoring_service():
    return ScoringService()

@pytest.fixture
def standard_policy():
    return ScoringPolicy(
        max_score_possible=100,
        penalty_per_attempt=10,
        time_bonus_threshold_seconds=60,
        time_bonus_value=15,
        allow_negative_score=False
    )

def test_calculate_score_simple(scoring_service, standard_policy):
    context = ScoringContext(
        base_points=50,
        attempts_count=1,
        elapsed_time_seconds=120, # Pas de bonus
        difficulty="Easy"
    )
    # 50 - (1 * 10) = 40
    assert scoring_service.calculate_score(context, standard_policy) == 40

def test_calculate_score_with_penalties(scoring_service, standard_policy):
    context = ScoringContext(
        base_points=80,
        attempts_count=4,
        elapsed_time_seconds=90,
        difficulty="Medium"
    )
    # 80 - (4 * 10) = 40
    assert scoring_service.calculate_score(context, standard_policy) == 40

def test_calculate_score_with_time_bonus(scoring_service, standard_policy):
    context = ScoringContext(
        base_points=50,
        attempts_count=0,
        elapsed_time_seconds=45, # <= 60s, bonus de 15
        difficulty="Hard"
    )
    # 50 + 15 = 65
    assert scoring_service.calculate_score(context, standard_policy) == 65

def test_calculate_score_combination_bonus_and_penalties(scoring_service, standard_policy):
    context = ScoringContext(
        base_points=70,
        attempts_count=2,
        elapsed_time_seconds=30, # Bonus 15
        difficulty="Medium"
    )
    # 70 - (2 * 10) + 15 = 50 + 15 = 65
    assert scoring_service.calculate_score(context, standard_policy) == 65

def test_score_minimum_zero(scoring_service, standard_policy):
    context = ScoringContext(
        base_points=20,
        attempts_count=5, # 5 * 10 = 50 de pénalité
        elapsed_time_seconds=150,
        difficulty="Easy"
    )
    # 20 - 50 = -30 -> bloqué à 0 car allow_negative_score=False
    assert scoring_service.calculate_score(context, standard_policy) == 0

def test_negative_score_allowed(scoring_service):
    policy = ScoringPolicy(
        max_score_possible=100,
        penalty_per_attempt=20,
        time_bonus_threshold_seconds=10,
        time_bonus_value=0,
        allow_negative_score=True
    )
    context = ScoringContext(
        base_points=10,
        attempts_count=3, # 3 * 20 = 60 de pénalité
        elapsed_time_seconds=50,
        difficulty="Hard"
    )
    # 10 - 60 = -50
    assert scoring_service.calculate_score(context, policy) == -50

def test_max_score_capped(scoring_service):
    policy = ScoringPolicy(
        max_score_possible=80, # Plafond max
        penalty_per_attempt=5,
        time_bonus_threshold_seconds=60,
        time_bonus_value=30,
        allow_negative_score=False
    )
    context = ScoringContext(
        base_points=70,
        attempts_count=0,
        elapsed_time_seconds=10, # Bonus 30 -> 70 + 30 = 100
        difficulty="Easy"
    )
    # Plafonné à 80
    assert scoring_service.calculate_score(context, policy) == 80

def test_invalid_context_raises_error(scoring_service, standard_policy):
    # Test base_points négatif
    with pytest.raises(InvalidScoreContext):
        scoring_service.calculate_score(
            ScoringContext(base_points=-10, attempts_count=1, elapsed_time_seconds=30, difficulty="Easy"),
            standard_policy
        )

    # Test attempts_count négatif
    with pytest.raises(InvalidScoreContext):
        scoring_service.calculate_score(
            ScoringContext(base_points=50, attempts_count=-2, elapsed_time_seconds=30, difficulty="Easy"),
            standard_policy
        )

    # Test elapsed_time_seconds négatif
    with pytest.raises(InvalidScoreContext):
        scoring_service.calculate_score(
            ScoringContext(base_points=50, attempts_count=1, elapsed_time_seconds=-5, difficulty="Easy"),
            standard_policy
        )