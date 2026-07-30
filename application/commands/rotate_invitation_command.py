from dataclasses import dataclass

@dataclass(frozen=True)
class RotateInvitationCommand:
    classroom_id: str
    teacher_id: str
    old_invitation_code: str
    validity_hours: int