import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

def create_resilient_sqlite_engine(db_url: str) -> Engine:
    """
    Crée un Engine SQLAlchemy explicitement configuré pour un environnement
    scolaire offline (haute concurrence d'accès sur fichier SQLite).
    """
    # L'Engine est créé de manière standard. 
    # Les optimisations seront injectées par l'écouteur d'événements ci-dessous.
    engine = create_engine(db_url)
    return engine

# Événement global SQLAlchemy déclenché à chaque nouvelle connexion DBAPI.
# Permet de configurer les PRAGMAs critiques AVANT que la transaction applicative ne débute.
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Injecte les PRAGMAs de résilience pour SQLite :
    - WAL : Autorise la lecture/écriture concurrente sans verrou exclusif immédiat.
    - busy_timeout : Patiente 5000ms au lieu d'échouer instantanément en cas de collision.
    - foreign_keys : Force l'intégrité référentielle (désactivée par défaut dans SQLite).
    """
    # Mesure de sécurité : ne s'applique que si le moteur sous-jacent est SQLite
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()