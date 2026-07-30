from dataclasses import dataclass

@dataclass(frozen=True)
class ClassroomName:
    value: str
    def __post_init__(self):
        name = self.value.strip()
        if len(name) < 3 or len(name) > 100:
            raise ValueError("Le nom de la classe doit contenir entre 3 et 100 caractères.")
        object.__setattr__(self, 'value', name)