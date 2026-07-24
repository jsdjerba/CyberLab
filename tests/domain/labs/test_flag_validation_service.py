import pytest
import hmac
from unittest.mock import patch
from domain.labs.services.flag_validation_service import FlagValidationService
from domain.labs.exceptions import InvalidFlagSubmission, SubmissionError

@pytest.fixture
def service():
    return FlagValidationService()

def test_exception_inheritance():
    assert issubclass(InvalidFlagSubmission, SubmissionError)

def test_normalize_standard_flag(service):
    raw = "  FLAG{abc_123}  "
    assert service.normalize_submission(raw) == "FLAG{abc_123}"

def test_normalize_preserves_internal_spaces(service):
    raw = "   FLAG{root shell}   "
    assert service.normalize_submission(raw) == "FLAG{root shell}"

def test_normalize_removes_control_characters(service):
    raw = "\tFLAG{abc}\n\r"
    assert service.normalize_submission(raw) == "FLAG{abc}"

def test_normalize_invalid_type(service):
    with pytest.raises(InvalidFlagSubmission):
        service.normalize_submission(None) # type: ignore

def test_validate_flag_identical(service):
    assert service.validate_flag("FLAG{abc}", "FLAG{abc}") is True

def test_validate_flag_different(service):
    assert service.validate_flag("FLAG{abc}", "FLAG{wrong}") is False

def test_validate_flag_case_insensitive_with_casefold(service):
    assert service.validate_flag("straße", "STRASSE") is True

def test_validate_flag_case_sensitive_strict(service):
    assert service.validate_flag("flag{abc}", "FLAG{abc}", case_sensitive=True) is False
    assert service.validate_flag("FLAG{abc}", "FLAG{abc}", case_sensitive=True) is True

def test_validate_flag_control_chars_and_formatting(service):
    submitted = "\t FLAG{cyber range} \n"
    expected = "FLAG{cyber range}"
    assert service.validate_flag(submitted, expected) is True

def test_validate_flag_empty_and_whitespace_only(service):
    assert service.validate_flag("", "") is True
    assert service.validate_flag("   \t\n", "") is True
    assert service.validate_flag("FLAG{abc}", "") is False

def test_validate_flag_none_raises_exception(service):
    with pytest.raises(InvalidFlagSubmission):
        service.validate_flag(None, "FLAG{abc}") # type: ignore
    with pytest.raises(InvalidFlagSubmission):
        service.validate_flag("FLAG{abc}", None) # type: ignore

def test_validate_flag_invalid_types_raises_exception(service):
    with pytest.raises(InvalidFlagSubmission):
        service.validate_flag(123, "FLAG{abc}") # type: ignore

def test_immutability_and_no_mutation_of_inputs(service):
    sub = "  FLAG{test test}\n"
    exp = "FLAG{test test}"
    sub_copy = sub
    exp_copy = exp
    
    service.validate_flag(sub, exp)
    
    assert sub == sub_copy
    assert exp == exp_copy

def test_hmac_compare_digest_is_invoked(service):
    with patch("hmac.compare_digest", wraps=hmac.compare_digest) as mocked_compare:
        result = service.validate_flag("FLAG{secure}", "FLAG{secure}")
        assert result is True
        mocked_compare.assert_called_once()

def test_very_long_strings(service):
    long_str = "A" * 10000
    assert service.validate_flag(long_str, long_str) is True