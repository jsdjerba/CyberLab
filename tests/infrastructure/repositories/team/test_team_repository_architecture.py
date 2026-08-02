# tests/infrastructure/repositories/team/test_team_repository_architecture.py
import inspect
from infrastructure.persistence.sqlite.team_repository import SqlAlchemyTeamRepository
from infrastructure.persistence.sqlite.team_query_repository import SqlAlchemyTeamQueryRepository

def test_command_repository_does_not_expose_sqlalchemy_models():
    sig = inspect.signature(SqlAlchemyTeamRepository.find_by_id)
    assert "TeamModel" not in str(sig.return_annotation)

def test_query_repository_does_not_depend_on_team_repository():
    source_code = inspect.getsource(SqlAlchemyTeamQueryRepository)
    assert "TeamRepository" not in source_code, "Le Read Side ne doit pas dépendre du Command Repository"
    assert "SqlAlchemyTeamRepository" not in source_code

def test_repository_mapping_isolation():
    repo_file = inspect.getfile(SqlAlchemyTeamRepository)
    assert "infrastructure\\persistence\\sqlite" in repo_file or "infrastructure/persistence/sqlite" in repo_file