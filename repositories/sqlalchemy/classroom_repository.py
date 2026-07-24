from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from database.models.classroom import Classroom
from repositories.base_repository import BaseRepository
from repositories.interfaces.classroom_repository_interface import IClassroomRepository

class ClassroomRepository(BaseRepository[Classroom], IClassroomRepository):
    def __init__(self, session: Session):
        super().__init__(session, Classroom)

    def get_by_join_code(self, code: str) -> Optional[Classroom]:
        stmt = select(Classroom).where(Classroom.join_code == code)
        return self.session.scalar(stmt)

    def get_by_teacher(self, teacher_id: int) -> List[Classroom]:
        stmt = select(Classroom).where(Classroom.teacher_id == teacher_id)
        return list(self.session.scalars(stmt).all())

    def create_classroom(self, classroom: Classroom) -> Classroom:
        return self.create(classroom)

    def get_classroom_statistics(self, classroom_id: int) -> dict:
        stmt = select(Classroom).options(selectinload(Classroom.enrollments)).where(Classroom.id == classroom_id)
        classroom = self.session.scalar(stmt)
        
        if not classroom:
            return {}
            
        return {
            "name": classroom.name,
            "total_students": len(classroom.enrollments),
            "created_at": classroom.created_at
        }