from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class StudentHistory:
    """Value Object immuable encapsulant l'historique de l'étudiant pour les évaluations."""
    completed_lab_count: int
    successful_lab_ids: Tuple[str, ...]
    current_streak: int = 0