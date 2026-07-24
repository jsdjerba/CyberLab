from dataclasses import dataclass

@dataclass(frozen=True)
class AchievementDTO:
    achievement_id: str
    title: str
    description: str
    unlocked: bool