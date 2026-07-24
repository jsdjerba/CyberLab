from typing import List
from domain.progress.entities.progress import Progress
from application.interfaces.progress_repository import IProgressRepository

class ProgressService:
    def __init__(self, progress_repo: IProgressRepository):
        self.progress_repo = progress_repo

    def start_lab(self, student_id: str, lab_id: str) -> Progress:
        existing_progress = self.progress_repo.get_by_student_and_lab(student_id, lab_id)
        if existing_progress:
            return existing_progress
            
        new_progress = Progress.start(student_id=student_id, lab_id=lab_id)
        self.progress_repo.save(new_progress)
        return new_progress

    def complete_lab(self, student_id: str, lab_id: str) -> Progress:
        progress = self.progress_repo.get_by_student_and_lab(student_id, lab_id)
        if not progress:
            raise ValueError(f"Progress not found for student {student_id} and lab {lab_id}")
            
        progress.complete()
        self.progress_repo.save(progress)
        
        # Les événements (comme LabCompletedEvent) sont accumulés dans l'entité
        # event_dispatcher.dispatch(progress.pull_events())
        
        return progress