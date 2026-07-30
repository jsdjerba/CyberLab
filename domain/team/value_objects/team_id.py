from dataclasses import dataclass

@dataclass(frozen=True)
class TeamId:
    """Value Object représentant l'identifiant unique d'une équipe."""
    value: str