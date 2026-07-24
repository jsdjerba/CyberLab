from dataclasses import dataclass

@dataclass(frozen=True)
class AchievementContext:
    student_id: int
    completed_labs_count: int
    total_xp: int