from dataclasses import dataclass, field



@dataclass
class StudentGamificationProfile:
    student_id: int
    total_xp: int = 0
    completed_labs_count: int = 0
    unlocked_badges: list[str] = field(default_factory=list)

@dataclass(frozen=True) # Correction 1
class Badge:
    badge_id: str
    name: str
    description: str
    icon: str
    xp_bonus: int

@dataclass(frozen=True) # Correction 2
class AchievementContext:
    student_id: int
    completed_labs_count: int
    total_xp: int