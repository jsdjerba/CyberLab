from dataclasses import dataclass
from domain.labs.value_objects.step_id import StepId

@dataclass(frozen=True)
class CompleteStepCommand:
    instance_id: str
    step_id: StepId