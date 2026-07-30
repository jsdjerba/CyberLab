"""
Port Repository pour LabInstance (Clean Architecture).
"""

from typing import Protocol, Optional
from domain.entities.lab_instance import LabInstance


class LabInstanceRepository(Protocol):
    def save(self, instance: LabInstance) -> None:
        ...

    def find_by_id(self, student_id: str, lab_id: str) -> Optional[LabInstance]:
        ...

    def delete(self, student_id: str, lab_id: str) -> None:
        ...

    def exists(self, student_id: str, lab_id: str) -> bool:
        ...