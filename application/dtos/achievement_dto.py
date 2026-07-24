from dataclasses import dataclass

@dataclass(frozen=True)
class AchievementDto:
    badge_id: str
    title: str
    description: str