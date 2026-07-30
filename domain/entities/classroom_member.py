from datetime import datetime
from domain.value_objects.student_id import StudentId

class ClassroomMember:
    def __init__(self, student_id: StudentId, joined_at: datetime):
        self.student_id = student_id
        self.joined_at = joined_at