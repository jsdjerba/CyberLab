from typing import Optional, Dict, Tuple
from application.labs.interfaces.lab_instance_repository import LabInstanceRepository
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId

class FakeLabInstanceRepository(LabInstanceRepository):
    def __init__(self):
        # Clé composée : (student_id, lab_id)
        self._instances: Dict[Tuple[int, str], LabInstance] = {}

    def save(self, instance: LabInstance) -> None:
        key = (instance.student_id.value, instance.lab_id.value)
        self._instances[key] = instance

    def get_by_student_and_lab(self, student_id: StudentId, lab_id: LabId) -> Optional[LabInstance]:
        key = (student_id.value, lab_id.value)
        return self._instances.get(key)