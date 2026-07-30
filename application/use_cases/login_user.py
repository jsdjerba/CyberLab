"""
Use Case de connexion d'un utilisateur existant.
"""
from typing import Optional
from application.dto.auth_dto import LoginUserCommand, AuthResultDTO
from application.ports.user_repository import UserRepository
from application.ports.password_hasher import PasswordHasher
from application.ports.token_provider import TokenProvider
from application.ports.unit_of_work import UnitOfWork
from domain.value_objects.email import Email
from domain.exceptions.auth_exceptions import UserNotFoundException, InvalidPasswordException


class LoginUserUseCase:
    def __init__(
        self, 
        repository: UserRepository, 
        hasher: PasswordHasher, 
        token_provider: TokenProvider, 
        uow: Optional[UnitOfWork] = None
    ):
        self._repository = repository
        self._hasher = hasher
        self._token_provider = token_provider
        self._uow = uow

    def execute(self, command: LoginUserCommand) -> AuthResultDTO:
        email = Email(command.email)
        
        # 1. Recherche de l'utilisateur
        user = self._repository.find_by_email(email.value)
        if not user:
            raise UserNotFoundException("Identifiants incorrects.")

        # 2. Vérification cryptographique via Port
        if not self._hasher.verify(command.password, user.password_hash):
            raise InvalidPasswordException("Identifiants incorrects.")

        # 3. Exécution de la logique métier de domaine
        user.login(current_time=command.current_time)

        # 4. Sauvegarde transactionnelle de l'état et des événements
        if self._uow:
            with self._uow:
                self._repository.save(user)
                self._uow.commit()
        else:
            self._repository.save(user)

        # 5. Génération du token de session via Port
        token = self._token_provider.create_token(user_id=user.user_id.value, role=user.role.value)

        return AuthResultDTO(
            user_id=user.user_id.value,
            email=user.email.value,
            role=user.role.value,
            token=token
        )