from dataclasses import dataclass

@dataclass(frozen=True)
class LabCompletedEvent:
    student_id: int
    lab_id: int
    xp_reward: int
    category: str
    difficulty: str