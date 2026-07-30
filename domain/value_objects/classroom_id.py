from dataclasses import dataclass

@dataclass(frozen=True)
class ClassroomId:
    value: str

    def __post_init__(self):
        if self.value is None or not str(self.value).strip():
            raise ValueError("ClassroomId ne peut pas être vide.")
        object.__setattr__(self, 'value', str(self.value).strip())