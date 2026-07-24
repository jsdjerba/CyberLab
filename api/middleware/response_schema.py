from typing import TypedDict, Any, Optional

class ErrorDetail(TypedDict):
    code: str
    message: str

class APIResponse(TypedDict):
    success: bool
    data: Any
    error: Optional[ErrorDetail]