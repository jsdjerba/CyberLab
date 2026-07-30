"""
Use Case d'inscription d'un nouvel utilisateur.
"""
from typing import Optional
from application.dto.auth_dto import RegisterUserCommand, AuthResultDTO
from application.ports.user_repository import UserRepository
from application.ports.password_hasher import PasswordHasher
from application.ports.id_generator import IdGenerator
from application.ports.unit_of_work import UnitOfWork
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.value_objects.role import Role
from domain.exceptions.auth_exceptions import DuplicateUserException


class RegisterUserUseCase:
    def __init__(
        self, 
        repository: UserRepository, 
        hasher: PasswordHasher, 
        id_generator: IdGenerator,
        uow: Optional[UnitOfWork] = None
    ):
        self._repository = repository
        self._hasher = hasher
        self._id_generator = id_generator
        self._uow = uow

    def execute(self, command: RegisterUserCommand) -> AuthResultDTO:
        target_email = Email(command.email)
        
        # 1. Vérification d'unicité préemptive
        if self._repository.exists(target_email.value):
            raise DuplicateUserException(f"Un utilisateur avec l'email {target_email.value} existe déjà.")

        # 2. Hachage sécurisé via Port infrastructurel
        pw_hash = self._hasher.hash(command.password)
        
        # 3. Génération d'identifiant déterministe via Port
        generated_id = command.user_id if command.user_id else self._id_generator.generate()
        uid = UserId(generated_id)
        role = Role(command.role)
        
        # 4. Instanciation métier via la Factory du Domaine
        user = User.register(
            user_id=uid,
            email=target_email,
            password_hash=pw_hash,
            role=role,
            current_time=command.current_time
        )

        # 5. Persistance transactionnelle
        if self._uow:
            with self._uow:
                self._repository.save(user)
                self._uow.commit()
        else:
            self._repository.save(user)

        return AuthResultDTO(
            user_id=user.user_id.value,
            email=user.email.value,
            role=user.role.value,
            token=None
        )