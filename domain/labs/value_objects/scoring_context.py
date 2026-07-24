from dataclasses import dataclass, field
from typing import List
from typing import Mapping, Any, Tuple

@dataclass(frozen=True)
class ScoringContext:
    """Encapsule tous les paramètres nécessaires au calcul d'un score."""
    base_points: int
    attempts_count: int
    elapsed_time_seconds: int
    difficulty: str
    bonuses_applied: Tuple[str, ...] = field(default_factory=tuple)
    penalties_applied: Tuple[str, ...] = field(default_factory=tuple)
    extra_metadata: Mapping[str, Any] = field(default_factory=dict)