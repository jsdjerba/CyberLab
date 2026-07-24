from dataclasses import dataclass
from domain.labs.exceptions import LabDomainError

@dataclass(frozen=True)
class StudentId:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise LabDomainError(f"Invalid Student ID: {self.value}")