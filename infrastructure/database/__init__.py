"""
Module de configuration de la base de données SQLAlchemy (Infrastructure).
Expose l'instance déclarative Base et les gestionnaires de sessions pour SQLite / PostgreSQL.
"""

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

# Instance déclarative de base pour les modèles ORM
Base = declarative_base()

# Configuration par défaut du moteur et de la session (SQLite local par défaut pour le mode Offline-First)
DATABASE_URL = "sqlite:///cyberlab.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite avec Flask/Threads multiples
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialise le schéma de la base de données en créant toutes les tables."""
    Base.metadata.create_all(bind=engine)