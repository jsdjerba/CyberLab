from datetime import datetime
from domain.value_objects.invitation_code import InvitationCode
from domain.value_objects.student_id import StudentId
from domain.enums.invitation_status import InvitationStatus

class Invitation:
    def __init__(self, code: InvitationCode, expires_at: datetime):
        self.code = code
        self.expires_at = expires_at
        self.status = InvitationStatus.PENDING
        self.used_by: StudentId | None = None

    def is_valid(self, current_time: datetime) -> bool:
        if self.status != InvitationStatus.PENDING:
            return False
        return current_time <= self.expires_at

    def accept(self, student_id: StudentId, current_time: datetime):
        if not self.is_valid(current_time):
            raise ValueError("L'invitation est invalide ou expirée.")
        self.status = InvitationStatus.ACCEPTED
        self.used_by = student_id

    def revoke(self):
        self.status = InvitationStatus.REVOKED