import pytest
from unittest.mock import Mock

from bootstrap.container import Container
from application.use_cases.start_lab_use_case import StartLabUseCase
from application.use_cases.submit_flag_use_case import SubmitFlagUseCase
from infrastructure.adapters.challenge_validation_adapter import ChallengeValidationAdapter
from infrastructure.repositories.sqlalchemy_lab_repository import SqlAlchemyLabRepository
from infrastructure.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository

def test_container_creates_start_lab_use_case():
    session = Mock()
    container = Container(session)
    
    use_case = container.start_lab_use_case()
    
    assert isinstance(use_case, StartLabUseCase)
    # Vérification que les dépendances ont bien été injectées
    assert isinstance(use_case._lab_repository, SqlAlchemyLabRepository)
    assert isinstance(use_case._lab_instance_repository, SqlAlchemyLabInstanceRepository)
    assert use_case._event_bus is container.event_bus()

def test_container_creates_submit_flag_use_case():
    session = Mock()
    container = Container(session)
    
    use_case = container.submit_flag_use_case()
    
    assert isinstance(use_case, SubmitFlagUseCase)
    # Vérification des composants critiques
    assert isinstance(use_case._challenge_validation_port, ChallengeValidationAdapter)
    assert isinstance(use_case._lab_repository, SqlAlchemyLabRepository)

def test_shared_singletons():
    session = Mock()
    container = Container(session)
    
    bus1 = container.event_bus()
    bus2 = container.event_bus()
    
    policy1 = container.attempt_policy_service()
    policy2 = container.attempt_policy_service()
    
    # Vérification de l'identité des instances (Singletons)
    assert bus1 is bus2
    assert policy1 is policy2

def test_session_scope():
    session = Mock()
    container = Container(session)
    
    lab_repo = container.lab_repository()
    lab_instance_repo = container.lab_instance_repository()
    student_repo = container.student_repository()
    
    # Vérification que les repositories partagent la même session injectée sans la recréer
    assert lab_repo._session is session
    assert lab_instance_repo._session is session
    assert student_repo._session is session