"""Port abstrait pour la persistance de l'agrégat Classroom."""
from typing import Protocol, Optional
from domain.entities.classroom import Classroom
from domain.value_objects.classroom_id import ClassroomId

class ClassroomRepository(Protocol):
    def save(self, classroom: Classroom) -> None:
        ...
        
    def find_by_id(self, classroom_id: ClassroomId) -> Optional[Classroom]:
        ...