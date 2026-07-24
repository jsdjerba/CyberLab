from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models.user import User
from database.models.enums import UserRole
from repositories.base_repository import BaseRepository
from repositories.interfaces.user_repository_interface import IUserRepository

class UserRepository(BaseRepository[User], IUserRepository):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        return self.session.scalar(stmt)

    def get_by_role(self, role: UserRole) -> List[User]:
        stmt = select(User).where(User.role == role)
        return list(self.session.scalars(stmt).all())

    def get_students(self) -> List[User]:
        return self.get_by_role(UserRole.STUDENT)

    def create_user(self, user: User) -> User:
        return self.create(user)

    def update_xp(self, user_id: int, new_xp: int) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.xp = new_xp
            self.session.flush()
        return user

    def increment_xp(self, user_id: int, amount: int) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.xp += amount
            self.session.flush()
        return user