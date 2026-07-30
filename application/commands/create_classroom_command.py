"""Commande immuable pour la création d'une salle de classe."""
from dataclasses import dataclass

@dataclass(frozen=True)
class CreateClassroomCommand:
    tenant_id: str
    name: str
    teacher_id: str
    max_students: int = 40
    allow_team_switch: bool = True
    allow_multiple_teachers: bool = False