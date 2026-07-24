from dataclasses import dataclass

@dataclass
class Lab:
    """Entité métier Lab."""
    lab_id: str
    title: str
    is_active: bool