from domain.dto.progress_dto import ProgressDTO

class ProgressMapper:
    @staticmethod
    def to_dto(model) -> ProgressDTO:
        return ProgressDTO(
            id=model.id,
            student_id=model.student_id,
            lab_id=model.lab_id,
            status=model.status,
            completed_at=model.completed_at,
            xp_earned=model.xp_earned
        )