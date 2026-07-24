from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enforces SQLite optimizations for performance and integrity.
    Triggers automatically whenever a new connection is made.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.close()

def get_engine(database_uri: str) -> Engine:
    """
    Creates and configures the SQLAlchemy engine.
    `check_same_thread=False` allows safe thread usage in Flask environments.
    """
    return create_engine(
        database_uri,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )