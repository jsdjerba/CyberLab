from typing import Optional, Dict
from application.labs.interfaces.lab_repository import LabRepository
from domain.labs.entities.lab import Lab
from domain.labs.value_objects.lab_id import LabId

class FakeLabRepository(LabRepository):
    def __init__(self):
        self._labs: Dict[str, Lab] = {}

    def add(self, lab: Lab) -> None:
        self._labs[lab.id.value] = lab

    def get_by_id(self, lab_id: LabId) -> Optional[Lab]:
        return self._labs.get(lab_id.value)