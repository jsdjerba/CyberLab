from dataclasses import dataclass

@dataclass(frozen=True)
class LabSummaryDTO:
    id: int
    title: str
    category: str
    difficulty: str
    xp_reward: int

@dataclass(frozen=True)
class LabDetailDTO:
    id: int
    title: str
    description: str
    xp_reward: int

@dataclass(frozen=True)
class LabProgressDTO:
    lab_id: int
    status: str
    started_at: str

@dataclass(frozen=True)
class FlagSubmissionResultDTO:
    success: bool
    message: str