import pytest
from datetime import datetime
from application.use_cases.submit_flag_use_case import SubmitFlagUseCase
from domain.exceptions import LabInstanceNotFoundError, LabNotFoundError
from application.dtos.validation_result_dto import ValidationResult

# --- Fakes alignés sur les contrats stricts de l'Application ---

class FakeAttemptPolicyService:
    def can_attempt(self, instance, step_id, policy, current_time) -> bool:
        return True

class FakeChallengeValidationPort:
    def __init__(self, result: ValidationResult):
        self.result = result
        
    def validate(self, lab_id: str, step_id: str, submitted_answer: str) -> ValidationResult:
        return self.result

class FakeScoringService:
    def calculate_score(self, base_points: int, attempts_count: int, elapsed_time_seconds: int) -> int:
        return base_points

# --- Dummies pour l'Infrastructure ---

class DummyLabRepo:
    def __init__(self, lab=None):
        self._lab = lab
    def get_by_id(self, lab_id):
        return self._lab

class DummyInstanceRepo:
    def __init__(self, instance=None):
        self._instance = instance
    def get_by_id(self, instance_id):
        return self._instance
    def save(self, instance):
        pass

class DummyStudentRepo:
    pass

class DummyEventBus:
    def publish(self, events):
        pass

# --- Mocks simples des entités pour le test ---

class DummyCommand:
    def __init__(self, instance_id, lab_id, step_id, submitted_flag):
        self.instance_id = instance_id
        self.lab_id = lab_id
        self.step_id = step_id
        self.submitted_flag = submitted_flag

class DummyStep:
    def __init__(self, step_id, points=10):
        self.id = step_id
        self.points = points

class DummyLab:
    def __init__(self, steps):
        self.steps = steps
    def get_step(self, step_id):
        for s in self.steps:
            if s.id == step_id:
                return s
        raise ValueError("Step not found")

class DummyInstance:
    def __init__(self):
        self.completed_steps = []
        self.attempts = {}
        self.score = 0
    
    def get_attempt_count(self, step_id):
        return self.attempts.get(step_id, 0)
        
    def complete_step(self, step_id, lab):
        self.completed_steps.append(step_id)

    def record_attempt(self, step_id, current_time):
        self.attempts[step_id] = self.attempts.get(step_id, 0) + 1
        
    def add_score(self, points):
        self.score += points

# --- Tests ---

def test_submit_flag_success_removes_duck_typing():
    # 1. Arrange
    command = DummyCommand(
        instance_id="inst_1", 
        lab_id="lab_1", 
        step_id="step_1", 
        submitted_flag="FLAG{correct}"
    )
    
    step = DummyStep(step_id="step_1")
    lab = DummyLab(steps=[step])
    instance = DummyInstance()
    
    use_case = SubmitFlagUseCase(
        lab_repository=DummyLabRepo(lab),
        lab_instance_repository=DummyInstanceRepo(instance),
        student_repository=DummyStudentRepo(),
        event_bus=DummyEventBus(),
        attempt_policy_service=FakeAttemptPolicyService(),
        challenge_validation_port=FakeChallengeValidationPort(ValidationResult(success=True)),
        scoring_service=FakeScoringService(),
        time_provider=lambda: datetime(2026, 1, 1) # Injection déterministe
    )

    # 2. Act
    result = use_case.execute(command)

    # 3. Assert
    assert result is True
    assert "step_1" in instance.completed_steps
    assert instance.get_attempt_count("step_1") == 0 # Pas de tentative ratée enregistrée
    assert instance.score == 10