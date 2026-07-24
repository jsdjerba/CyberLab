from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from repositories.base_repository import BaseRepository
from repositories.mappers.progress_persistence_mapper import ProgressPersistenceMapper
from domain.progress.entities.progress import Progress as DomainProgress
from database.models.progress import Progress as ProgressDB
from database.models.user import User as UserModel
from database.models.lab import Lab as LabModel

class ProgressRepository(BaseRepository[DomainProgress]):
    def __init__(self, session: Session):
        super().__init__(session, ProgressDB)
        self.session = session
        self.mapper = ProgressPersistenceMapper()

    def _get_tech_ids(self, student_id: str, lab_id: str) -> tuple[int, int]:
        user = self.session.query(UserModel).filter_by(domain_id=student_id).first()
        lab = self.session.query(LabModel).filter_by(lab_id=lab_id).first()
        if not user or not lab:
            raise ValueError(f"Identifiants métier invalides : student={student_id}, lab={lab_id}")
        return user.id, lab.id

    def save(self, progress: DomainProgress) -> None:
        stmt = select(ProgressDB).where(ProgressDB.domain_id == progress.progress_id)
        result = self.session.execute(stmt).scalar_one_or_none()
        
        if not result:
            tech_user_id, tech_lab_id = self._get_tech_ids(progress.student_id, progress.lab_id)
            new_record = self.mapper.to_model(progress, tech_user_id, tech_lab_id)
            self.session.add(new_record)
        else:
            self.mapper.update_model(result, progress)
        self.session.flush()

    def get_by_id(self, progress_id: str) -> Optional[DomainProgress]:
        stmt = select(ProgressDB).where(ProgressDB.domain_id == progress_id)
        db_model = self.session.execute(stmt).scalar_one_or_none()
        return self.mapper.to_domain(db_model) if db_model else None

    def get_by_student_and_lab(self, student_id: str, lab_id: str) -> Optional[DomainProgress]:
        tech_user_id, tech_lab_id = self._get_tech_ids(student_id, lab_id)
        stmt = select(ProgressDB).where(ProgressDB.user_id == tech_user_id, ProgressDB.lab_id == tech_lab_id)
        db_model = self.session.execute(stmt).scalar_one_or_none()
        return self.mapper.to_domain(db_model) if db_model else None

    def list_by_student(self, student_id: str) -> List[DomainProgress]:
        user = self.session.query(UserModel).filter_by(domain_id=student_id).first()
        if not user: return []
        stmt = select(ProgressDB).where(ProgressDB.user_id == user.id)
        results = self.session.execute(stmt).scalars().all()
        return [self.mapper.to_domain(m) for m in results]