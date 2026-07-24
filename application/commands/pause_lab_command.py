from dataclasses import dataclass

@dataclass(frozen=True)
class PauseLabCommand:
    instance_id: str