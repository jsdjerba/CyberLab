import pytest
from sqlalchemy import text
from infrastructure.persistence.sqlite.database import create_sqlite_engine

def test_database_engine_can_initialize(tmp_path):
    db_path = tmp_path / "test_init.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    assert engine is not None

def test_sqlite_foreign_keys_are_enabled(tmp_path):
    db_path = tmp_path / "test_fk.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA foreign_keys;")).scalar()
        assert result == 1, "Foreign Keys must be strictly enabled (1) at connection level."

def test_sqlite_wal_mode_is_enabled(tmp_path):
    db_path = tmp_path / "test_wal.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA journal_mode;")).scalar()
        assert result.lower() == "wal", "WAL mode must be enabled for concurrent Read/Write."

def test_sqlite_synchronous_mode_is_normal(tmp_path):
    db_path = tmp_path / "test_sync.db"
    engine = create_sqlite_engine(f"sqlite:///{db_path}")
    
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA synchronous;")).scalar()
        # En SQLite, NORMAL = 1, FULL = 2. On attend NORMAL pour préserver la carte SD.
        assert result == 1, "Synchronous mode must be NORMAL (1) to prevent SD card wear."