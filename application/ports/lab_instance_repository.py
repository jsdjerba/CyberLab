from typing import Protocol, Optional
from domain.labs.entities.lab_instance import LabInstance

class LabInstanceRepository(Protocol):
    def get_by_id(self, instance_id: str) -> Optional[LabInstance]:
        ...
    def save(self, instance: LabInstance) -> None:
        ...