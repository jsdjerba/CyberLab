from dataclasses import dataclass

@dataclass(frozen=True)
class RevokeInvitationCommand:
    classroom_id: str
    teacher_id: str
    invitation_code: str