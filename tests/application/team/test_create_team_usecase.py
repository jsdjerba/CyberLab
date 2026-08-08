import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from application.use_cases.create_team import CreateTeamUseCase
# L'import statique sécurisé de la commande
try:
    from application.commands.create_team_command import CreateTeamCommand
except ImportError:
    from application.team.commands.create_team_command import CreateTeamCommand

from domain.team.aggregate import Team
# Importation indispensable du Value Object pour respecter le contrat
from domain.team.value_objects.team_color import TeamColor


@pytest.fixture
def mock_repo():
    return Mock()

@pytest.fixture
def mock_clock():
    clock = Mock()
    clock.now.return_value = datetime(2026, 8, 6, 12, 0, 0)
    return clock

@pytest.fixture
def mock_id_gen():
    id_gen = Mock()
    # Le use case génère deux IDs : un pour le team_id, un pour l'event_id
    id_gen.generate.side_effect = ["team-uuid-1", "event-uuid-1"]
    return id_gen

@pytest.fixture
def mock_uow():
    uow = MagicMock()
    # Configuration du Context Manager (with self._uow:)
    uow.__enter__.return_value = uow
    return uow

@pytest.fixture
def mock_retry_policy():
    policy = Mock()
    # Simule l'exécution synchrone et immédiate de la fonction passée à la RetryPolicy
    policy.execute.side_effect = lambda f: f()
    return policy

@pytest.fixture
def use_case(mock_repo, mock_clock, mock_id_gen, mock_uow, mock_retry_policy):
    return CreateTeamUseCase(
        repository=mock_repo,
        clock=mock_clock,
        id_generator=mock_id_gen,
        unit_of_work=mock_uow,
        retry_policy=mock_retry_policy
    )

def create_valid_command():
    """Utilitaire pour instancier la commande de test en respectant les signatures variables."""
    # CORRECTION ARCHITECTURALE : Utilisation de l'Enum TeamColor("RED") au lieu de "RED"
    valid_color = TeamColor("RED")
    
    try:
        return CreateTeamCommand(
            team_id="t1", 
            classroom_id="class-1", 
            color=valid_color, 
            max_size=4
        )
    except TypeError:
        # Fallback si la commande n'accepte pas team_id (car généré par le Use Case)
        return CreateTeamCommand(
            classroom_id="class-1", 
            color=valid_color, 
            max_size=4
        )

def test_create_team_calls_domain_factory(use_case, mock_id_gen, mock_clock):
    # Arrangement
    command = create_valid_command()

    # Action
    response = use_case.execute(command)

    # Assertions
    assert response.status == "SUCCESS"
    assert response.team_id == "team-uuid-1"
    assert response.event_id == "event-uuid-1"
    assert mock_id_gen.generate.call_count == 2
    assert mock_clock.now.call_count == 1

def test_create_team_registers_events_and_commits(use_case, mock_uow, mock_repo):
    # Arrangement
    command = create_valid_command()

    # Action
    use_case.execute(command)

    # Assertions liées à la persistance
    mock_repo.save.assert_called_once()
    saved_team = mock_repo.save.call_args[0][0]
    
    # Vérification que l'objet sauvegardé est bien une instance de l'agrégat
    assert isinstance(saved_team, Team)
    
    # Assertions liées aux événements de domaine et à la transaction
    mock_uow.register_events.assert_called_once()
    events = mock_uow.register_events.call_args[0][0]
    
    # Team.create(...) génère exactement un événement (TeamCreatedEvent)
    assert len(events) == 1 
    
    # La transaction doit être validée
    mock_uow.commit.assert_called_once()