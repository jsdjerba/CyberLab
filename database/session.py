import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session

def get_engine(db_url: str = "sqlite:///cyberlab.db"):
    return create_engine(db_url, connect_args={"check_same_thread": False})

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

def get_session_factory(engine: Engine):
    """Retourne une session scopée supportant .remove()"""
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return scoped_session(factory)

def initialize_session(engine: Engine):
    return get_session_factory(engine)