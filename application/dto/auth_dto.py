"""
Data Transfer Objects pour l'authentification (Couche Application).
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    password: str
    role: str
    current_time: datetime
    user_id: Optional[str] = None

@dataclass(frozen=True)
class LoginUserCommand:
    email: str
    password: str
    current_time: datetime

@dataclass(frozen=True)
class AuthResultDTO:
    user_id: str
    email: str
    role: str
    token: Optional[str] = None