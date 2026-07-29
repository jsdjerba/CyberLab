from dataclasses import dataclass

@dataclass(frozen=True)
class CompletedLabId:
    """
    Value Object représentant l'identifiant d'un laboratoire validé.
    Garantit qu'un ID vide ou mal formé ne peut pas exister dans le domaine.
    """
    value: str

    def __post_init__(self):
        if not self.value or not str(self.value).strip():
            raise ValueError("L'identifiant du laboratoire ne peut pas être vide.")