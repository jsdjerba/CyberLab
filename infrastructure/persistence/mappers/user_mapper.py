"""
Anti-Corruption Layer (ACL) : Convertit l'ORM en Entité pure et inversement.
"""
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.password_hash import PasswordHash
from domain.value_objects.role import Role
from infrastructure.persistence.models.user_model import UserModel

class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            user_id=UserId(model.id),
            email=Email(model.email),
            password_hash=PasswordHash(model.password_hash),
            role=Role(model.role),
            is_active=model.is_active
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.user_id.value,
            email=entity.email.value,
            password_hash=entity.password_hash.value,
            role=entity.role.value,
            is_active=entity.is_active
        )