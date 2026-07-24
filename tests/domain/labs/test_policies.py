import pytest
from domain.labs.policies.submission_policy import SubmissionPolicy
from domain.labs.policies.grading_policy import GradingPolicy
from domain.labs.exceptions import InvalidSubmissionPolicy

def test_submission_policy_no_limit():
    policy = SubmissionPolicy(max_attempts=None, cooldown_seconds=0)
    assert policy.max_attempts is None

def test_submission_policy_under_limit():
    policy = SubmissionPolicy(max_attempts=3, cooldown_seconds=0)
    assert policy.max_attempts == 3

def test_submission_policy_invalid():
    with pytest.raises(InvalidSubmissionPolicy):
        SubmissionPolicy(max_attempts=-1, cooldown_seconds=0)

def test_grading_policy():
    policy = GradingPolicy()
    
    assert policy.calculate_xp(10, 1) == 10
    assert policy.calculate_xp(10, 2) == 7
    assert policy.calculate_xp(10, 3) == 5
    assert policy.calculate_xp(10, 10) == 5
    assert policy.calculate_xp(0, 1) == 0