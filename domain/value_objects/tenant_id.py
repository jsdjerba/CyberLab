from dataclasses import dataclass

@dataclass(frozen=True)
class TenantId:
    value: str = "DEFAULT"

    def __post_init__(self):
        if self.value is None or not str(self.value).strip():
            raise ValueError("TenantId ne peut pas être vide.")
        object.__setattr__(self, 'value', str(self.value).strip())