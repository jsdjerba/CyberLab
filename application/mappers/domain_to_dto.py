from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.achievement import Achievement
from application.dtos.lab_result_dto import LabResultDto
from application.dtos.achievement_dto import AchievementDto

class DomainToDtoMapper:
    """Mapper pur pour transformer les entités/value objects du domaine en DTOs d'application."""

    @staticmethod
    def to_lab_result_dto(instance: LabInstance) -> LabResultDto:
        return LabResultDto(
            instance_id=str(instance.id),
            lab_id=str(instance.lab_id),
            status="FINISHED" if getattr(instance, "is_finished", False) else "IN_PROGRESS",
            score=getattr(instance, "score", 0),
            is_finished=getattr(instance, "is_finished", False)
        )

    @staticmethod
    def to_achievement_dto(achievement: Achievement) -> AchievementDto:
        return AchievementDto(
            badge_id=str(achievement.badge_id),
            title=achievement.title,
            description=achievement.description
        )