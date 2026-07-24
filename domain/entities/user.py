from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class User:
    """Entité métier User. Totalement ignorante de l'ORM."""
    username: str
    password_hash: str
    domain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    xp: int = field(default=0)
    badges: List[str] = field(default_factory=list)

    @classmethod
    def create(cls, username: str, password_hash: str) -> "User":
        return cls(username=username, password_hash=password_hash)

    def add_xp(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("XP amount cannot be negative")
        self.xp += amount

    def check_achievements(self) -> List[str]:
        """Logique métier d'attribution de badges internes."""
        new_badges = []
        if self.xp >= 100 and "NOVICE" not in self.badges:
            self.badges.append("NOVICE")
            new_badges.append("NOVICE")
        return new_badges