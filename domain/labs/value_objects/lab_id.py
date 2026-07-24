import re
from dataclasses import dataclass
from domain.labs.exceptions import LabDomainError

@dataclass(frozen=True)
class LabId:
    value: str

    def __post_init__(self):
        if not self.value or not re.match(r"^[a-zA-Z0-9_]+$", self.value):
            raise LabDomainError(f"Invalid Lab ID format: {self.value}")