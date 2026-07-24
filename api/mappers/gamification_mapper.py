from domain.dto.gamification_response_dto import GamificationProfileDTO, BadgeDisplayDTO, LeaderboardEntryDTO
from typing import List

class GamificationMapper:
    @staticmethod
    def to_badges_list(badges: List[BadgeDisplayDTO]) -> list[dict]:
        return [{"id": b.id, "name": b.name} for b in badges]

    @staticmethod
    def to_profile_dict(dto: GamificationProfileDTO) -> dict:
        return {
            "student_id": dto.student_id,
            "total_xp": dto.total_xp,
            "completed_labs": dto.completed_labs,
            "badges": GamificationMapper.to_badges_list(dto.badges)
        }

    @staticmethod
    def to_leaderboard_list(dtos: list[LeaderboardEntryDTO]) -> list[dict]:
        return [{"username": e.username, "total_xp": e.total_xp} for e in dtos]