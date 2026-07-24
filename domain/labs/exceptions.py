from typing import Any, Optional

class LabDomainError(Exception):
    """Exception racine pour le domaine des laboratoires."""
    pass

# ==========================================
# Lifecycle Errors
# ==========================================
class LifecycleError(LabDomainError):
    pass

class LabAlreadyStarted(LifecycleError):
    def __init__(self, message: str = "Le laboratoire est déjà démarré."):
        super().__init__(message)

class LabNotStarted(LifecycleError):
    def __init__(self, message: str = "Le laboratoire n'a pas encore démarré."):
        super().__init__(message)

class InvalidLabTransition(LifecycleError):
    def __init__(self, current_state: Any, requested_state: Any, message: Optional[str] = None):
        self.current_state = current_state
        self.requested_state = requested_state
        super().__init__(
            message or f"Transition d'état invalide : impossible de passer de {current_state} à {requested_state}."
        )

# ==========================================
# Scoring Errors
# ==========================================
class ScoringError(LabDomainError):
    pass

class InvalidScoreContext(ScoringError):
    def __init__(self, message: str = "Le contexte de scoring est invalide (valeurs négatives non autorisées)."):
        super().__init__(message)

class NegativeScoreNotAllowed(ScoringError):
    def __init__(self, message: str = "Le score négatif n'est pas autorisé par la politique de notation."):
        super().__init__(message)

# ==========================================
# Submission & Policy Errors
# ==========================================
class SubmissionError(LabDomainError):
    pass

class InvalidFlagSubmission(SubmissionError):
    pass

class SubmissionPolicyError(SubmissionError):
    pass

class MaxAttemptsReached(SubmissionPolicyError):
    def __init__(self, step_id: Any, attempts_count: int, max_attempts: Optional[int], message: Optional[str] = None):
        self.step_id = step_id
        self.attempts_count = attempts_count
        self.max_attempts = max_attempts
        super().__init__(
            message or f"Nombre maximum d'essais atteint ({attempts_count}/{max_attempts}) pour l'étape {step_id}."
        )

class CooldownActive(SubmissionPolicyError):
    def __init__(self, step_id: Any, remaining_seconds: int, message: Optional[str] = None):
        self.step_id = step_id
        self.remaining_seconds = remaining_seconds
        super().__init__(
            message or f"Cooldown actif pour l'étape {step_id}. Veuillez patienter {remaining_seconds}s."
        )

class InvalidSubmissionPolicy(SubmissionPolicyError):
    def __init__(self, message: str = "La politique de soumission est invalide (valeurs négatives interdites)."):
        super().__init__(message)

# ==========================================
# Eligibility Errors
# ==========================================
class EligibilityError(LabDomainError):
    pass

class PrerequisitesNotMet(EligibilityError):
    def __init__(self, prerequisite_id: str, message: Optional[str] = None):
        self.prerequisite_id = prerequisite_id
        super().__init__(message or f"Prérequis non satisfait : {prerequisite_id}")

class LabNotPublished(EligibilityError):
    def __init__(self, lab_id: Any, message: Optional[str] = None):
        self.lab_id = lab_id
        super().__init__(message or f"Le laboratoire {lab_id} n'est pas publié.")

class AccessDenied(EligibilityError):
    pass

class ClassroomClosed(EligibilityError):
    pass

# ==========================================
# Rétrocompatibilité
# ==========================================
class StepNotFound(LabDomainError):
    pass

class InvalidStepTransition(LabDomainError):
    pass

class StepAlreadyCompleted(LabDomainError):
    pass

class InvalidLabState(LabDomainError):
    pass