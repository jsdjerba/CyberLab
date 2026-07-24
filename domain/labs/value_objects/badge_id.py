from dataclasses import dataclass

@dataclass(frozen=True)
class BadgeId:
    """Value Object immuable représentant l'identifiant d'un badge."""
    value: str

    def __str__(self) -> str:
        return self.value