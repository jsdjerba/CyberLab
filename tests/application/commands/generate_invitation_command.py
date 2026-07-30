from dataclasses import dataclass

@dataclass(frozen=True)
class GenerateInvitationCommand:
    classroom_id: str
    teacher_id: str
    validity_hours: int