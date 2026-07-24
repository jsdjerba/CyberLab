from dataclasses import dataclass

@dataclass(frozen=True)
class AbandonLabCommand:
    instance_id: str