from domain.progress.entities.progress import Progress as DomainProgress
from domain.progress.value_objects.progress_status import ProgressStatus
from database.models.progress import Progress as ProgressDB
from database.models.enums import LabStatus

class ProgressPersistenceMapper:
    @staticmethod
    def to_domain(model: ProgressDB) -> DomainProgress:
        status_mapping = {
            LabStatus.NOT_STARTED: ProgressStatus.STARTED,
            LabStatus.IN_PROGRESS: ProgressStatus.STARTED,
            LabStatus.COMPLETED: ProgressStatus.COMPLETED,
        }
        return DomainProgress(
            progress_id=model.domain_id,
            student_id=model.user.domain_id,
            lab_id=model.lab.lab_id,
            status=status_mapping.get(model.status, ProgressStatus.STARTED),
            started_at=model.started_at,
            completed_at=model.completed_at
        )

    @staticmethod
    def to_model(progress: DomainProgress, tech_user_id: int, tech_lab_id: int) -> ProgressDB:
        status_mapping = {
            ProgressStatus.STARTED: LabStatus.IN_PROGRESS,
            ProgressStatus.COMPLETED: LabStatus.COMPLETED,
        }
        return ProgressDB(
            domain_id=progress.progress_id,
            user_id=tech_user_id,
            lab_id=tech_lab_id,
            status=status_mapping.get(progress.status, LabStatus.IN_PROGRESS),
            started_at=progress.started_at,
            completed_at=progress.completed_at
        )

    @staticmethod
    def update_model(model: ProgressDB, progress: DomainProgress) -> None:
        status_mapping = {
            ProgressStatus.STARTED: LabStatus.IN_PROGRESS,
            ProgressStatus.COMPLETED: LabStatus.COMPLETED,
        }
        model.status = status_mapping.get(progress.status, LabStatus.IN_PROGRESS)
        model.completed_at = progress.completed_at