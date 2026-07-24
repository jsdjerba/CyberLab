from dataclasses import dataclass
from domain.labs.value_objects.step_id import StepId

@dataclass(frozen=True)
class SubmitFlagCommand:
    instance_id: str
    step_id: StepId
    submitted_flag: str