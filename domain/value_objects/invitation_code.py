from dataclasses import dataclass

@dataclass(frozen=True)
class InvitationCode:
    value: str
    def __post_init__(self):
        val = self.value.upper().strip()
        if len(val) < 6:
            raise ValueError("L'InvitationCode doit contenir au moins 6 caractères.")
        if not val.isalnum():
            raise ValueError("L'InvitationCode doit être alphanumérique.")
        if any(c in val for c in "O0I1L"):
            raise ValueError("L'InvitationCode contient des caractères ambigus (O, 0, I, 1, L).")
        object.__setattr__(self, 'value', val)