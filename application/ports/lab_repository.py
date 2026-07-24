from typing import Protocol, Optional
from domain.labs.entities.lab import Lab
from domain.labs.value_objects.lab_id import LabId

class LabRepository(Protocol):
    def get_by_id(self, lab_id: LabId) -> Optional[Lab]:
        ...