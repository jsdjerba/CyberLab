"""
Conteneur d'injection de dépendances simple et explicite (Pure Python / No Framework).
Assemble l'infrastructure et la couche application pour l'API et les services.
"""

from typing import Any
from infrastructure.persistence.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from application.use_cases.start_lab import StartLabUseCase
from application.use_cases.submit_flag import SubmitFlagUseCase


class Container:
    """
    Conteneur central gérant le cycle de vie des repositories et des use cases.
    """

    def __init__(self, session: Any, validator: Any = None):
        self._session = session
        self._validator = validator
        self._repository = SqlAlchemyLabInstanceRepository(session)

    @property
    def repository(self) -> SqlAlchemyLabInstanceRepository:
        return self._repository

    def start_lab_use_case(self) -> StartLabUseCase:
        return StartLabUseCase(self._repository)

    def submit_flag_use_case(self) -> SubmitFlagUseCase:
        # Fournit un validateur par défaut si non spécifié
        validator = self._validator if self._validator else self._default_validator()
        return SubmitFlagUseCase(self._repository, validator)

    def _default_validator(self) -> Any:
        class DefaultValidator:
            def validate(self, flag: str, objective_id: Any) -> bool:
                return "secret" in str(flag).lower() or "flag" in str(flag).lower()
        return DefaultValidator()