
class DomainException(Exception):
    """Base class for all domain-level exceptions. Compatible with api.middleware.error_handler."""
    code: str = "DOMAIN_ERROR"

class InvalidProgressTransitionError(DomainException):
    code = "INVALID_PROGRESS_TRANSITION"

class LabAlreadyCompletedError(DomainException):
    code = "LAB_ALREADY_COMPLETED"

class UnauthorizedProgressAccessError(DomainException):
    code = "UNAUTHORIZED_PROGRESS_ACCESS"

class ProgressNotFoundError(DomainException):
    code = "PROGRESS_NOT_FOUND"
