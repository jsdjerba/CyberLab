from dataclasses import dataclass

@dataclass(frozen=True)
class StudentId:
    """Value Object représentant la référence vers un étudiant global."""
    value: str