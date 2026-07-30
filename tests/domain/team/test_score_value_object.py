import pytest
from domain.team.value_objects.score import Score
from domain.team.exceptions.team_exceptions import NegativeScoreException, InvalidPointsException

def test_score_initializes_to_zero():
    score = Score(0)
    assert score.value == 0

def test_score_rejects_negative_initialization():
    with pytest.raises(NegativeScoreException):
        Score(-10)

def test_score_add_points_returns_new_score():
    score = Score(100)
    new_score = score.add(20)
    assert new_score.value == 120
    assert score.value == 100 # Immutability check

def test_score_rejects_adding_negative_points():
    score = Score(100)
    with pytest.raises(InvalidPointsException):
        score.add(-10)

def test_score_subtract_points():
    score = Score(10)
    new_score = score.subtract(5)
    assert new_score.value == 5

def test_score_subtract_below_zero_raises_exception():
    score = Score(10)
    with pytest.raises(NegativeScoreException):
        score.subtract(20)