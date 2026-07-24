import pytest
from typing import Optional
from domain.entities.user import User
from domain.exceptions import InvalidCredentials, UserAlreadyExists
from application.services.auth_service import AuthService

class FakeUserRepository:
    def __init__(self):
        self.users = {}

    def get_by_username(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def get_by_domain_id(self, domain_id: str) -> Optional[User]:
        for u in self.users.values():
            if u.domain_id == domain_id: 
                return u
        return None

    def save(self, user: User) -> None:
        self.users[user.username] = user

class FakePasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed_{password}"

    def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed_{password}"

def test_register_success():
    repo = FakeUserRepository()
    hasher = FakePasswordHasher()
    service = AuthService(repo, hasher)

    user = service.register("student1", "password123")

    assert user.username == "student1"
    assert user.password_hash == "hashed_password123"
    assert repo.get_by_username("student1") is not None

def test_authenticate_success():
    repo = FakeUserRepository()
    hasher = FakePasswordHasher()
    service = AuthService(repo, hasher)
    service.register("student1", "password123")

    token = service.authenticate("student1", "password123")
    
    assert token is not None

def test_authenticate_failure_wrong_password():
    repo = FakeUserRepository()
    hasher = FakePasswordHasher()
    service = AuthService(repo, hasher)
    service.register("student1", "password123")

    # Vérification stricte du contrat : le service doit lever InvalidCredentials
    with pytest.raises(InvalidCredentials):
        service.authenticate("student1", "wrongpass")