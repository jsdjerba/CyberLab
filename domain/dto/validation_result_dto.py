from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationResultDTO:
    success: bool
    student_id: int
    lab_id: int
    xp_to_award: int
    message: str