from dataclasses import dataclass

@dataclass(frozen=True)
class ClassroomId:
    """Value Object représentant la référence (Soft Link) vers la Classroom parente."""
    value: str