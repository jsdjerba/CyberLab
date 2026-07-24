from dataclasses import dataclass

@dataclass(frozen=True)
class GamificationResultDTO:
    student_id: int
    xp_added: int
    badges_unlocked: list[str]