from domain.labs.exceptions import SubmissionError

class InvalidFlagSubmission(SubmissionError):
    """Levée lorsqu'une soumission de flag est invalide."""
    pass