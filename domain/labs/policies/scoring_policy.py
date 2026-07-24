from dataclasses import dataclass

@dataclass(frozen=True)
class ScoringPolicy:
    """Règles de calcul applicables à une instance de laboratoire."""
    max_score_possible: int
    penalty_per_attempt: int
    time_bonus_threshold_seconds: int
    time_bonus_value: int
    allow_negative_score: bool = False