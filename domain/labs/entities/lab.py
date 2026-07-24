from typing import List
from dataclasses import dataclass

from domain.labs.entities.step import Step
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.exceptions import StepNotFound

@dataclass(frozen=True)
class Lab:
    id: LabId
    title: str
    description: str
    difficulty: str
    duration: int
    steps: List[Step]

    def get_step(self, step_id: StepId) -> Step:
        for step in self.steps:
            if step.id == step_id:
                return step
        raise StepNotFound(f"Step '{step_id.value}' not found in lab '{self.id.value}'")

    def total_points(self) -> int:
        return sum(step.points for step in self.steps)

    def number_of_steps(self) -> int:
        return len(self.steps)