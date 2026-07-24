from abc import ABC, abstractmethod
from typing import Optional
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId

class LabInstanceRepository(ABC):
    @abstractmethod
    def get_by_student_and_lab(self, student_id: StudentId, lab_id: LabId) -> Optional[LabInstance]:
        """Récupère l'instance en cours pour un étudiant et un lab."""
        pass

    @abstractmethod
    def save(self, instance: LabInstance) -> None:
        """Sauvegarde ou met à jour l'instance."""
        pass