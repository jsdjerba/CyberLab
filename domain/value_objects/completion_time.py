from dataclasses import dataclass
from datetime import timedelta

@dataclass(frozen=True, slots=True)
class CompletionTime:
    duration: timedelta

    def __post_init__(self):
        # Autorise == 0 (la triche temporelle est gérée par la politique d'AntiCheat, pas le VO)
        if self.duration.total_seconds() < 0:
            raise ValueError("La durée ne peut pas être négative.")