"""DTO de réponse pour découpler l'entité Domain des couches externes."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ClassroomResponseDTO:
    classroom_id: str
    tenant_id: str
    name: str
    status: str
    primary_teacher_id: str