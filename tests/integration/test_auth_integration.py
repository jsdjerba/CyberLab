import pytest
from typing import Optional
from domain.entities.user import User
from domain.exceptions import InvalidCredentials, UserAlreadyExists
from application.services.auth_service import AuthService

# --- Fakes pour isoler le test de l'implémentation SQLAlchemy ---

class FakeIntegrationUserRepository:
    def __init__(self):
        self.users = {}

    def get_by_username(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def save(self, user: User) -> None:
        self.users[user.username] = user

class FakeIntegrationPasswordHasher:
    def hash(self, password: str) -> str:
        return f"integrated_hash_{password}"

    def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"integrated_hash_{password}"


# --- Test du flux complet ---

def test_auth_full_flow(session):
    # Injection des Fakes (la fixture 'session' est gardée pour pytest, mais on simule le repo)
    user_repo = FakeIntegrationUserRepository()
    hasher = FakeIntegrationPasswordHasher()
    service = AuthService(user_repo, hasher)

    # 1. Inscription d'un nouvel utilisateur
    user = service.register(username="admin_test", raw_password="SecurePassword123")
    assert user.username == "admin_test"

    # 2. Authentification réussie
    token = service.authenticate(username="admin_test", raw_password="SecurePassword123")
    assert token is not None

    # 3. Authentification en échec (mauvais mot de passe)
    with pytest.raises(InvalidCredentials):
        service.authenticate(username="admin_test", raw_password="WrongPassword")

    # 4. Inscription en échec (l'utilisateur existe déjà)
    with pytest.raises(UserAlreadyExists):
        service.register(username="admin_test", raw_password="AnotherPassword")