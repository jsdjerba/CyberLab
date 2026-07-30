from typing import Protocol, Optional
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email

class UserRepository(Protocol):
    """Port du domaine pour la persistance des utilisateurs."""
    
    def save(self, user: User) -> None:
        ...

    def find_by_id(self, user_id: UserId) -> Optional[User]:
        ...

    def find_by_email(self, email: Email) -> Optional[User]:
        ...