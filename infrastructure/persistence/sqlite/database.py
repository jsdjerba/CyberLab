from sqlalchemy import create_engine, event
from sqlalchemy.pool import NullPool
from sqlalchemy.engine.interfaces import DBAPIConnection

def _set_sqlite_pragma(dbapi_connection: DBAPIConnection, connection_record: getattr) -> None:
    """
    Injecte les configurations vitales (ADR 07.1-1) à chaque nouvelle ouverture de fichier.
    Optimise les performances I/O et préserve la carte SD (synchronous=NORMAL).
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

def create_sqlite_engine(database_url: str):
    """
    Crée le moteur SQLAlchemy.
    NullPool garantit qu'aucune connexion n'est gardée ouverte entre les requêtes.
    """
    engine = create_engine(
        database_url,
        poolclass=NullPool,
    )
    
    # Attachement de l'événement de connexion pour exécuter les PRAGMAs
    event.listen(engine, "connect", _set_sqlite_pragma)
    
    return engine