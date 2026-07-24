from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class EligibilityContext:
    """Contexte environnemental pour évaluer l'accès d'un étudiant."""
    student_level: str
    active_classroom_id: str
    completed_lab_ids: List[str]