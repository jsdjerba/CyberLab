from typing import Protocol, Optional
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.student_history import StudentHistory

class StudentRepository(Protocol):
    def get_history(self, student_id: StudentId) -> Optional[StudentHistory]:
        ...