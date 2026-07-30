"""DTO de réponse pour l'inscription d'un étudiant."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class EnrollmentResponseDTO:
    classroom_id: str
    student_id: str
    joined_at: datetime
    team_id: Optional[str] = None