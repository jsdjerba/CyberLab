import inspect
import sys
from infrastructure.persistence.sqlite.team_repository import SqlAlchemyTeamRepository
from infrastructure.persistence.sqlite.team_query_repository import SqlAlchemyTeamQueryRepository

def test_team_repository_does_not_reference_outbox():
    """Vérifie que le TeamRepository ignore totalement l'existence de l'outbox."""
    source = inspect.getsource(SqlAlchemyTeamRepository)
    assert "outbox" not in source.lower()
    assert "Outbox" not in source

def test_query_repository_does_not_reference_outbox():
    """Vérifie que le Query Repository ignore totalement l'existence de l'outbox."""
    source = inspect.getsource(SqlAlchemyTeamQueryRepository)
    assert "outbox" not in source.lower()
    assert "Outbox" not in source

def test_domain_has_no_sqlalchemy_dependency():
    """Vérifie que le domaine ne référence jamais SQLAlchemy."""
    import domain.team.aggregate as agg_module
    source = inspect.getsource(agg_module)
    assert "sqlalchemy" not in source.lower()

def test_domain_events_are_not_serialized_in_domain():
    """Vérifie que le domaine n'effectue aucune sérialisation JSON pour l'outbox."""
    import domain.team.aggregate as agg_module
    source = inspect.getsource(agg_module)
    assert "json" not in source.lower()

def test_no_retry_policy_exists():
    """Vérifie le respect strict du YAGNI : absence de module de politique de retry dans infrastructure."""
    import infrastructure
    modules = [m for m in sys.modules.keys() if m.startswith("infrastructure") and ("retry" in m or "backoff" in m)]
    assert len(modules) == 0

def test_no_dead_letter_queue_exists():
    """Vérifie l'absence de table ou de logique de Dead Letter Queue (YAGNI)."""
    from infrastructure.persistence.sqlite import models
    mapper = models.Base.metadata.tables
    assert "dead_letter_queue" not in mapper
    assert "dlq" not in mapper