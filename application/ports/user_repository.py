"""
Port Application unifié pour la persistance des utilisateurs.
"""
from typing import Protocol, Optional
from domain.entities.user import User


class UserRepository(Protocol):
    def save(self, user: User) -> None:
        ...

    def find_by_id(self, user_id: str) -> Optional[User]:
        ...

    def find_by_email(self, email: str) -> Optional[User]:
        ...

    def exists(self, email: str) -> bool:
        ...