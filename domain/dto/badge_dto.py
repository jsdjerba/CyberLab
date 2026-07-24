from dataclasses import dataclass

@dataclass(frozen=True)
class BadgeDTO:
    badge_id: str
    name: str
    description: str
    icon: str
    xp_bonus: int