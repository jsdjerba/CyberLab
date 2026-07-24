from typing import Optional
from domain.entities.user import User
from domain.exceptions import UserAlreadyExists, InvalidCredentials
from application.interfaces.user_repository import IUserRepository
from application.security.password_hasher import PasswordHasher

class AuthService:
    def __init__(self, user_repo: IUserRepository, hasher: PasswordHasher):
        self.user_repo = user_repo
        self.hasher = hasher

    def register(self, username: str, raw_password: str) -> User:
        if self.user_repo.get_by_username(username):
            raise UserAlreadyExists(f"Username '{username}' already exists.")
        hashed = self.hasher.hash(raw_password)
        new_user = User.create(username=username, password_hash=hashed)
        self.user_repo.save(new_user)
        return new_user

    def authenticate(self, username: str, raw_password: str) -> str:
        user = self.user_repo.get_by_username(username)
        if not user or not self.hasher.verify(raw_password, user.password_hash):
            raise InvalidCredentials("Invalid username or password.")
        return "mock_token"