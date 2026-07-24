import pytest
from typing import Optional, List
from domain.progress.entities.progress import Progress
from domain.progress.value_objects.progress_status import ProgressStatus
from application.services.progress_service import ProgressService

class FakeProgressRepository:
    def __init__(self):
        self.progresses = {}
        
    def get_by_id(self, progress_id: str) -> Optional[Progress]:
        return self.progresses.get(progress_id)
        
    def get_by_student_and_lab(self, student_id: str, lab_id: str) -> Optional[Progress]:
        for p in self.progresses.values():
            if p.student_id == student_id and p.lab_id == lab_id:
                return p
        return None
        
    def list_by_student(self, student_id: str) -> List[Progress]:
        return [p for p in self.progresses.values() if p.student_id == student_id]
        
    def save(self, progress: Progress) -> None:
        self.progresses[progress.progress_id] = progress

def test_start_lab():
    repo = FakeProgressRepository()
    service = ProgressService(repo)
    
    progress = service.start_lab("user-123", "HTTP_01")
    
    assert progress.student_id == "user-123"
    assert progress.lab_id == "HTTP_01"
    assert progress.status == ProgressStatus.STARTED

def test_complete_lab():
    repo = FakeProgressRepository()
    service = ProgressService(repo)
    service.start_lab("user-123", "HTTP_01")
    
    progress = service.complete_lab("user-123", "HTTP_01")
    
    assert progress.status == ProgressStatus.COMPLETED
    assert len(progress.pull_events()) == 1