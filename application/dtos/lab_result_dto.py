from dataclasses import dataclass

@dataclass(frozen=True)
class LabResultDto:
    instance_id: str
    lab_id: str
    status: str
    score: int
    is_finished: bool