from datetime import datetime
from domain.value_objects.teacher_id import TeacherId
from domain.enums.instructor_role import InstructorRole

class ClassroomInstructor:
    def __init__(self, teacher_id: TeacherId, role: InstructorRole, assigned_at: datetime):
        self.teacher_id = teacher_id
        self.role = role
        self.assigned_at = assigned_at