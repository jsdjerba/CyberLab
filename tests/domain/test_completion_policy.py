import pytest

from domain.policies.completion_policy import SingleObjectivePolicy, AllObjectivesPolicy, ScoreBasedPolicy
from domain.entities.objective import Objective
from domain.value_objects.objective_id import ObjectiveId


@pytest.fixture
def mock_objectives():
    return [
        Objective(objective_id=ObjectiveId("obj-1"), score_weight=30),
        Objective(objective_id=ObjectiveId("obj-2"), score_weight=50),
        Objective(objective_id=ObjectiveId("obj-3"), score_weight=20)
    ]


def test_single_objective_policy(mock_objectives):
    policy = SingleObjectivePolicy()
    
    assert policy.is_complete(completed_objectives=[], all_objectives=mock_objectives) is False
    assert policy.is_complete(completed_objectives=[ObjectiveId("obj-2")], all_objectives=mock_objectives) is True


def test_all_objectives_policy(mock_objectives):
    policy = AllObjectivesPolicy()
    
    # Partiel
    completed_partial = [ObjectiveId("obj-1"), ObjectiveId("obj-2")]
    assert policy.is_complete(completed_objectives=completed_partial, all_objectives=mock_objectives) is False
    
    # Total
    completed_all = [ObjectiveId("obj-1"), ObjectiveId("obj-2"), ObjectiveId("obj-3")]
    assert policy.is_complete(completed_objectives=completed_all, all_objectives=mock_objectives) is True


def test_score_based_policy(mock_objectives):
    policy = ScoreBasedPolicy(required_score=80)
    
    # 30 + 20 = 50 (< 80)
    assert policy.is_complete(completed_objectives=[ObjectiveId("obj-1"), ObjectiveId("obj-3")], all_objectives=mock_objectives) is False
    
    # 30 + 50 = 80 (>= 80)
    assert policy.is_complete(completed_objectives=[ObjectiveId("obj-1"), ObjectiveId("obj-2")], all_objectives=mock_objectives) is True