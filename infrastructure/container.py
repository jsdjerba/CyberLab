"""
Conteneur d'injection de dépendances centralisé (Enterprise Grade).
"""

from typing import Any, Optional
from sqlalchemy.orm import Session
from infrastructure.database import SessionLocal
from infrastructure.persistence.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from infrastructure.transaction.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork

# --- Nouveaux imports Phase 5.3 (Infrastructure Auth) ---
from infrastructure.identity.uuid_id_generator import UuidIdGenerator
from infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from infrastructure.security.jwt_token_provider import JwtTokenProvider
from infrastructure.persistence.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository

from application.use_cases.create_lab_instance import CreateLabInstanceUseCase
from application.use_cases.start_lab import StartLabUseCase
from application.use_cases.submit_flag import SubmitFlagUseCase
from application.use_cases.get_lab_instance import GetLabInstanceUseCase

# --- Nouveaux imports Phase 5.2 (Use Cases Auth) ---
from application.use_cases.register_user import RegisterUserUseCase
from application.use_cases.login_user import LoginUserUseCase


class ApplicationContainer:
    """Conteneur d'injection de dépendances instanciable par requête."""

    def __init__(self, session: Optional[Session] = None, validator: Optional[Any] = None):
        self._session = session if session else SessionLocal()
        
        # --- Dépendances existantes (Lab) ---
        self._repository = SqlAlchemyLabInstanceRepository(self._session)
        self._uow = SqlAlchemyUnitOfWork(self._session)
        self._validator = validator

        # --- Nouvelles dépendances (Auth Phase 5.3) ---
        self._user_repository = SqlAlchemyUserRepository(self._session)
        self._password_hasher = BcryptPasswordHasher()
        self._id_generator = UuidIdGenerator()
        # En production, ce secret devra être injecté via les variables d'environnement (min 32 caractères)
        self._token_provider = JwtTokenProvider(secret="cyberlab-super-secret-key-for-2026-minimum-32-bytes")

    @property
    def session(self) -> Session:
        return self._session

    @property
    def repository(self) -> SqlAlchemyLabInstanceRepository:
        return self._repository

    # --- Factory Methods (Lab) ---
    def create_lab_instance_use_case(self) -> CreateLabInstanceUseCase:
        return CreateLabInstanceUseCase(self._repository, self._uow)

    def start_lab_use_case(self) -> StartLabUseCase:
        return StartLabUseCase(self._repository, self._uow)

    def submit_flag_use_case(self) -> SubmitFlagUseCase:
        validator = self._validator if self._validator else self._default_validator()
        return SubmitFlagUseCase(self._repository, validator, self._uow)

    def get_lab_instance_use_case(self) -> GetLabInstanceUseCase:
        return GetLabInstanceUseCase(self._repository)

    # --- Factory Methods (Auth) ---
    def register_user_use_case(self) -> RegisterUserUseCase:
        return RegisterUserUseCase(
            repository=self._user_repository,
            hasher=self._password_hasher,
            id_generator=self._id_generator,
            uow=self._uow
        )

    def login_user_use_case(self) -> LoginUserUseCase:
        return LoginUserUseCase(
            repository=self._user_repository,
            hasher=self._password_hasher,
            token_provider=self._token_provider,
            uow=self._uow
        )

    def _default_validator(self) -> Any:
        class DefaultCTFValidator:
            def validate(self, submitted_flag: str, objective_id: Any) -> bool:
                return "ctf{" in submitted_flag.lower() and "secret" in submitted_flag.lower()
        return DefaultCTFValidator()

    def close(self):
        if self._session:
            self._session.close()