from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class ValidationResult:
    success: bool
    reason: Optional[str] = None