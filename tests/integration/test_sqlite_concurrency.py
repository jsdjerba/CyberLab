import pytest
import tempfile
import os
import concurrent.futures
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from infrastructure.persistence.database_setup import create_resilient_sqlite_engine
from application.common.retry_policy import retry_on_db_locked

Base = declarative_base()

class ConcurrencyTestModel(Base):
    """Modèle factice dédié au test de stress concurrent."""
    __tablename__ = 'concurrency_test'
    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer)

@pytest.fixture
def stress_test_db():
    """Prépare une base de données physique SQLite avec la configuration de résilience."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    engine = create_resilient_sqlite_engine(f"sqlite:///{path}")
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Nettoyage sécurisé Windows (WinError 32)
    engine.dispose()
    for ext in ["", "-wal", "-shm"]:
        file_path = path + ext
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                pass

def test_sqlite_handles_30_concurrent_writes(stress_test_db):
    """
    Simule 30 étudiants (threads) tentant d'écrire simultanément dans la base.
    Valide l'efficacité combinée du mode WAL, du busy_timeout et de la Retry Policy.
    """
    # 1. Définition du worker avec notre Retry Policy applicative
    @retry_on_db_locked(max_attempts=10, base_delay=0.1)
    def student_worker(worker_id: int):
        # Chaque étudiant ouvre sa propre session (transaction)
        with Session(stress_test_db) as session:
            session.add(ConcurrencyTestModel(worker_id=worker_id))
            session.commit()
            return f"Success {worker_id}"

    nb_students = 30
    
    # 2. Lancement de l'attaque concurrente (30 threads en parallèle)
    with concurrent.futures.ThreadPoolExecutor(max_workers=nb_students) as executor:
        # Soumission de tous les jobs simultanément
        futures = [executor.submit(student_worker, i) for i in range(nb_students)]
        
        # Attente des résultats. Si la base bloque définitivement, future.result() 
        # soulèvera une exception sqlite3.OperationalError et fera échouer le test.
        for future in concurrent.futures.as_completed(futures):
            assert "Success" in future.result()

    # 3. Vérification de l'intégrité finale des données
    with Session(stress_test_db) as session:
        count = session.query(ConcurrencyTestModel).count()
        # Les 30 enregistrements doivent être présents, aucune perte n'est tolérée
        assert count == nb_students