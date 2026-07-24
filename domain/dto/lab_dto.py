from dataclasses import dataclass

@dataclass(frozen=True)
class LabDTO:
    id: int
    lab_id: str
    title: str
    category: str
    difficulty: str
    xp_reward: int
    is_active: bool