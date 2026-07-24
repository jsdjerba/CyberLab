from dataclasses import dataclass
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.step_type import StepType

@dataclass(frozen=True)
class Step:
    id: StepId
    type: StepType
    title: str
    points: int