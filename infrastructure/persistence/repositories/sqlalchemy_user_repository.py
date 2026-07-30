"""
Implémentation SQLAlchemy du Port UserRepository.
"""
from typing import Optional
from sqlalchemy.orm import Session
from application.ports.user_repository import UserRepository
from domain.entities.user import User
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.mappers.user_mapper import UserMapper

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    def save(self, user: User) -> None:
        model = UserMapper.to_model(user)
        self._session.merge(model)

    def find_by_id(self, user_id: str) -> Optional[User]:
        model = self._session.query(UserModel).filter_by(id=user_id).first()
        return UserMapper.to_domain(model) if model else None

    def find_by_email(self, email: str) -> Optional[User]:
        model = self._session.query(UserModel).filter_by(email=email.lower()).first()
        return UserMapper.to_domain(model) if model else None

    def exists(self, email: str) -> bool:
        return self._session.query(UserModel).filter_by(email=email.lower()).first() is not None