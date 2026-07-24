from dataclasses import dataclass

@dataclass(frozen=True)
class UserDTO:
    id: int
    username: str
    email: str

@dataclass(frozen=True)
class AuthTokenDTO:
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 7200