from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class InvitationResponseDTO:
    invitation_code: str
    classroom_id: str
    expires_at: datetime
    status: str
    event_version: int