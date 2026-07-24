import pytest
from dataclasses import FrozenInstanceError

from domain.labs.services.eligibility_service import LabEligibilityService
from domain.labs.entities.lab import Lab
from domain.labs.entities.step import Step
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.step_type import StepType
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.eligibility_context import EligibilityContext
from domain.labs.exceptions import LabNotPublished, PrerequisitesNotMet, AccessDenied

VALID_LAB_ID = "VALID_LAB_123"

@pytest.fixture
def eligibility_service():
    return LabEligibilityService()

@pytest.fixture
def sample_lab():
    return Lab(
        id=LabId(VALID_LAB_ID),
        title="Intro Lab",
        description="Test",
        difficulty="BEGINNER",
        duration=30,
        steps=[Step(StepId("s1"), StepType.FLAG, "F1", 10)],
        is_published=True,
        required_level="BEGINNER",
        required_lab_ids=(),
        allowed_classrooms=("CLASS_A", "CLASS_B")
    )

def test_beginner_authorized_access(eligibility_service, sample_lab):
    context = EligibilityContext(
        student_level="BEGINNER",
        active_classroom_id="CLASS_A",
        completed_lab_ids=()
    )
    assert eligibility_service.check_eligibility(StudentId(1), sample_lab, context) is True

def test_refuse_unpublished_lab(eligibility_service):
    lab = Lab(
        id=LabId(VALID_LAB_ID), title="Unpublished", description="", difficulty="BEGINNER", duration=10, steps=[],
        is_published=False
    )
    context = EligibilityContext("BEGINNER", "CLASS_A", ())
    with pytest.raises(LabNotPublished):
        eligibility_service.check_eligibility(StudentId(1), lab, context)

def test_refuse_insufficient_level(eligibility_service, sample_lab):
    sample_lab._required_level = "ADVANCED"
    context = EligibilityContext(
        student_level="BEGINNER",
        active_classroom_id="CLASS_A",
        completed_lab_ids=()
    )
    with pytest.raises(AccessDenied):
        eligibility_service.check_eligibility(StudentId(1), sample_lab, context)

def test_advanced_accepted_on_beginner_lab(eligibility_service, sample_lab):
    sample_lab._required_level = "BEGINNER"
    context = EligibilityContext(
        student_level="ADVANCED",
        active_classroom_id="CLASS_A",
        completed_lab_ids=()
    )
    assert eligibility_service.check_eligibility(StudentId(1), sample_lab, context) is True

def test_expert_accepted_on_advanced_lab(eligibility_service):
    lab = Lab(
        id=LabId(VALID_LAB_ID), title="Adv Lab", description="", difficulty="ADVANCED", duration=10, steps=[],
        required_level="ADVANCED"
    )
    context = EligibilityContext(
        student_level="EXPERT",
        active_classroom_id="CLASS_A",
        completed_lab_ids=()
    )
    assert eligibility_service.check_eligibility(StudentId(1), lab, context) is True

def test_missing_prerequisite(eligibility_service):
    lab = Lab(
        id=LabId(VALID_LAB_ID), title="Req Lab", description="", difficulty="BEGINNER", duration=10, steps=[],
        required_lab_ids=("LAB_PRE_01",)
    )
    context = EligibilityContext("BEGINNER", "CLASS_A", completed_lab_ids=("OTHER_LAB",))
    with pytest.raises(PrerequisitesNotMet) as exc_info:
        eligibility_service.check_eligibility(StudentId(1), lab, context)
    assert "LAB_PRE_01" in str(exc_info.value)

def test_all_prerequisites_validated(eligibility_service):
    lab = Lab(
        id=LabId(VALID_LAB_ID), title="Req Lab", description="", difficulty="BEGINNER", duration=10, steps=[],
        required_lab_ids=("LAB_PRE_01", "LAB_PRE_02")
    )
    context = EligibilityContext("BEGINNER", "CLASS_A", completed_lab_ids=("LAB_PRE_01", "LAB_PRE_02"))
    assert eligibility_service.check_eligibility(StudentId(1), lab, context) is True

def test_authorized_classroom(eligibility_service, sample_lab):
    context = EligibilityContext("BEGINNER", "CLASS_B", ())
    assert eligibility_service.check_eligibility(StudentId(1), sample_lab, context) is True

def test_refused_classroom(eligibility_service, sample_lab):
    context = EligibilityContext("BEGINNER", "CLASS_UNAUTHORIZED", ())
    with pytest.raises(AccessDenied):
        eligibility_service.check_eligibility(StudentId(1), sample_lab, context)

def test_eligibility_context_is_immutable():
    context = EligibilityContext("BEGINNER", "CLASS_A", ("LAB_1",))
    with pytest.raises(FrozenInstanceError):
        context.student_level = "EXPERT" # type: ignore

def test_no_side_effects_on_lab(eligibility_service, sample_lab):
    original_title = sample_lab.title
    original_published = sample_lab.is_published
    
    context = EligibilityContext("BEGINNER", "CLASS_A", ())
    eligibility_service.check_eligibility(StudentId(1), sample_lab, context)
    
    assert sample_lab.title == original_title
    assert sample_lab.is_published == original_published

def test_multiple_independent_labs(eligibility_service):
    lab1 = Lab(LabId(VALID_LAB_ID), "L1", "", "BEGINNER", 10, [], required_level="BEGINNER", allowed_classrooms=("C1",))
    lab2 = Lab(LabId("VALID_LAB_456"), "L2", "", "EXPERT", 10, [], required_level="EXPERT", allowed_classrooms=("C1",))

    ctx = EligibilityContext("BEGINNER", "C1", ())
    
    assert eligibility_service.check_eligibility(StudentId(1), lab1, ctx) is True
    with pytest.raises(AccessDenied):
        eligibility_service.check_eligibility(StudentId(1), lab2, ctx)