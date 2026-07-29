"""
Domain Service : Politique de régulation des tentatives (Anti-Abuse & Anti-Bruteforce).
Stateless, déterministe (injection temporelle) et immuable.
"""

from dataclasses import dataclass
from datetime import datetime

from domain.entities.attempt import Attempt
from domain.exceptions import LabLockedOutException, CooldownException


@dataclass(frozen=True, kw_only=True)
class AttemptPolicy:
    max_attempts: int
    cooldown_seconds: int
    lockout_duration_minutes: int

    def can_attempt(self, history: list[Attempt], current_time: datetime) -> bool:
        """
        Détermine si une nouvelle tentative est autorisée.
        Lève des exceptions de domaine (Fail-Fast) en cas de violation.
        """
        # 1. Protection Anti-Bruteforce (Lockout)
        incorrect_attempts = [attempt for attempt in history if not attempt.is_correct]
        if len(incorrect_attempts) >= self.max_attempts:
            raise LabLockedOutException("Nombre maximum de tentatives atteint")

        # 2. Protection Anti-Spam (Cooldown)
        if history:
            last_attempt = max(history, key=lambda a: a.timestamp)
            delta_seconds = (current_time - last_attempt.timestamp).total_seconds()
            
            if delta_seconds < self.cooldown_seconds:
                raise CooldownException("Veuillez patienter avant la prochaine tentative")

        return True