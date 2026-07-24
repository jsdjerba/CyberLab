class BaseDomainException(Exception): pass
class ValidationError(BaseDomainException): pass
class InvalidCredentials(BaseDomainException): pass
class LabNotFound(BaseDomainException): pass
class InvalidFlag(BaseDomainException): pass
class ProgressAlreadyCompleted(BaseDomainException): pass
class UserAlreadyExists(BaseDomainException): pass
# Ajout des exceptions manquantes pour Progress
class InvalidProgressTransitionError(BaseDomainException): pass
class LabAlreadyCompletedError(BaseDomainException): pass

