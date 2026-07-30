from dataclasses import dataclass

@dataclass(frozen=True)
class UserId:
    value: str

    def __post_init__(self):
        if not self.value or not str(self.value).strip():
            raise ValueError("UserId ne peut pas être vide.")