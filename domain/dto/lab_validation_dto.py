from dataclasses import dataclass

@dataclass(frozen=True)
class LabValidationDTO:
    id: int
    lab_id: str
    flag_hash: str
    is_active: bool
    xp_reward: int