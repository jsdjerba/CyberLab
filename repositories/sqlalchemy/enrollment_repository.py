from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from database.models.enrollment import Enrollment
from repositories.base_repository import BaseRepository
from repositories.interfaces.enrollment_repository_interface import IEnrollmentRepository
from core.exceptions import DuplicateEnrollmentException

class EnrollmentRepository(BaseRepository[Enrollment], IEnrollmentRepository):
    def __init__(self, session: Session):
        super().__init__(session, Enrollment)

    def enroll_student(self, user_id: int, classroom_id: int) -> Enrollment:
        enrollment = Enrollment(user_id=user_id, classroom_id=classroom_id)
        try:
            return self.create(enrollment)
        except IntegrityError as e:
            raise DuplicateEnrollmentException("Student already enrolled in this classroom") from e

    def is_student_enrolled(self, user_id: int, classroom_id: int) -> bool:
        stmt = select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.classroom_id == classroom_id
        )
        return self.session.scalar(stmt) is not None

    def get_student_classrooms(self, user_id: int) -> List[Enrollment]:
        stmt = select(Enrollment).options(selectinload(Enrollment.classroom)).where(Enrollment.user_id == user_id)
        return list(self.session.scalars(stmt).all())

    def get_classroom_students(self, classroom_id: int) -> List[Enrollment]:
        stmt = select(Enrollment).options(selectinload(Enrollment.user)).where(Enrollment.classroom_id == classroom_id)
        return list(self.session.scalars(stmt).all())