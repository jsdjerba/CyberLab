from dataclasses import dataclass
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId

@dataclass(frozen=True)
class StartLabCommand:
    student_id: StudentId
    lab_id: LabId