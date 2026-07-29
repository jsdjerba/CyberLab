from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class LabId:
    value: str

    def __post_init__(self):
        if not self.value or not str(self.value).strip():
            raise ValueError("L'identifiant ne peut pas être vide.")