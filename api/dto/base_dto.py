from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class ApiResponseDTO:
    success: bool
    code: str
    message: str
    data: Optional[Any] = field(default=None)
