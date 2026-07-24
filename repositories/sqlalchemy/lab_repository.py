from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models.lab import Lab
from repositories.base_repository import BaseRepository
from repositories.interfaces.lab_repository_interface import ILabRepository

class LabRepository(BaseRepository[Lab], ILabRepository):
    def __init__(self, session: Session):
        super().__init__(session, Lab)

    def get_by_lab_id(self, manifest_id: str) -> Optional[Lab]:
        stmt = select(Lab).where(Lab.lab_id == manifest_id)
        return self.session.scalar(stmt)

    def get_active_labs(self) -> List[Lab]:
        stmt = select(Lab).where(Lab.is_active == True)
        return list(self.session.scalars(stmt).all())

    def get_by_category(self, category: str) -> List[Lab]:
        stmt = select(Lab).where(Lab.category == category, Lab.is_active == True)
        return list(self.session.scalars(stmt).all())

    def set_lab_status(self, lab_id: int, status: bool) -> bool:
        lab = self.get_by_id(lab_id)
        if lab:
            lab.is_active = status
            self.session.flush()
            return True
        return False

    def activate_lab(self, lab_id: int) -> bool:
        return self.set_lab_status(lab_id, True)

    def disable_lab(self, lab_id: int) -> bool:
        return self.set_lab_status(lab_id, False)