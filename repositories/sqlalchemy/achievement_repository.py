from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from database.models.achievement import Achievement, UserAchievement
from repositories.base_repository import BaseRepository
from repositories.interfaces.achievement_repository_interface import IAchievementRepository
from core.exceptions import DuplicateAchievementException

class AchievementRepository(BaseRepository[Achievement], IAchievementRepository):
    def __init__(self, session: Session):
        super().__init__(session, Achievement)

    def get_user_badges(self, user_id: int) -> List[UserAchievement]:
        stmt = select(UserAchievement).options(selectinload(UserAchievement.achievement)).where(UserAchievement.user_id == user_id)
        return list(self.session.scalars(stmt).all())

    def award_badge(self, user_id: int, achievement_id: int) -> UserAchievement:
        award = UserAchievement(user_id=user_id, achievement_id=achievement_id)
        try:
            self.session.add(award)
            self.session.flush()
            return award
        except IntegrityError as e:
            raise DuplicateAchievementException("User already owns this badge") from e

    def has_badge(self, user_id: int, achievement_id: int) -> bool:
        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id
        )
        return self.session.scalar(stmt) is not None