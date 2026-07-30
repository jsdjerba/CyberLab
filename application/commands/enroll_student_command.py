"""Commande immuable pour l'inscription d'un étudiant à une classe."""
from dataclasses import dataclass

@dataclass(frozen=True)
class EnrollStudentCommand:
    classroom_id: str
    student_id: str
    invitation_code: str