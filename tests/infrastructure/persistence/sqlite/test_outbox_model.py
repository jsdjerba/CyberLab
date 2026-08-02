import pytest
from sqlalchemy import inspect
from infrastructure.persistence.sqlite.database import create_sqlite_engine
from infrastructure.persistence.sqlite.models import Base
# IMPORT ANTICIPÉ POUR PROVOQUER LE RED STATE
from infrastructure.persistence.sqlite.outbox_model import OutboxEventModel

@pytest.fixture
def sqlite_engine(tmp_path):
    db_path = tmp_path / "test_outbox_schema.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine

def test_outbox_table_schema(sqlite_engine):
    """Vérifie que la table outbox_events possède toutes les colonnes obligatoires."""
    inspector = inspect(sqlite_engine)
    assert "outbox_events" in inspector.get_table_names()
    columns = {col["name"] for col in inspector.get_columns("outbox_events")}
    expected = {
        "id", "aggregate_type", "aggregate_id", "event_type",
        "event_version", "payload", "occurred_at", "processed_at"
    }
    assert expected.issubset(columns)

def test_outbox_primary_key(sqlite_engine):
    """Vérifie que la colonne id est la clé primaire."""
    inspector = inspect(sqlite_engine)
    pk = inspector.get_pk_constraint("outbox_events")
    assert pk["constrained_columns"] == ["id"]

def test_outbox_processed_at_nullable(sqlite_engine):
    """Vérifie que processed_at est nullable par défaut (événement non traité)."""
    inspector = inspect(sqlite_engine)
    cols = {col["name"]: col for col in inspector.get_columns("outbox_events")}
    assert cols["processed_at"]["nullable"] is True

def test_outbox_partial_index_documented(sqlite_engine):
    """Vérifie la présence d'un index sur processed_at pour optimiser la recherche des non-traités."""
    inspector = inspect(sqlite_engine)
    indexes = inspector.get_indexes("outbox_events")
    index_names = {idx["name"] for idx in indexes}
    # Doit contenir un index dédié aux événements non traités
    assert any("outbox" in name for name in index_names)