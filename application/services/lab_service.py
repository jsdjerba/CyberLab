from typing import List, Optional
from domain.entities.lab import Lab
from application.interfaces.lab_repository import ILabRepository

class LabService:
    def __init__(self, lab_repo: ILabRepository):
        self.lab_repo = lab_repo

    def get_available_labs(self) -> List[Lab]:
        return self.lab_repo.list_available()

    def get_lab_details(self, lab_id: str) -> Optional[Lab]:
        return self.lab_repo.get_by_id(lab_id)