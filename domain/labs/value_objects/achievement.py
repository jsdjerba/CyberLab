from dataclasses import dataclass
from domain.labs.value_objects.badge_id import BadgeId

@dataclass(frozen=True)
class Achievement:
    """Value Object immuable représentant un accomplissement débloqué."""
    badge_id: BadgeId
    title: str
    description: str