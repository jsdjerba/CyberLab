from dataclasses import dataclass

@dataclass(frozen=True)
class ClassroomSettings:
    max_students: int = 40
    allow_team_switch: bool = True
    allow_multiple_teachers: bool = False