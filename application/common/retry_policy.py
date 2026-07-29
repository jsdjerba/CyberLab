import sqlite3
import time
import logging
import functools
import random
from typing import Callable, Any

logger = logging.getLogger(__name__)

def retry_on_db_locked(
    max_attempts: int = 5, 
    base_delay: float = 0.1, 
    max_delay: float = 2.0
) -> Callable:
    """
    Décorateur applicatif générique pour intercepter l'erreur SQLite 'database is locked'.
    Applique un mécanisme de Retry avec Backoff Exponentiel et Jitter aléatoire 
    pour éviter l'effet de troupeau (thundering herd) sans dépendance d'infrastructure lourde.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    # On intercepte uniquement le verrou SQLite
                    if "database is locked" in str(e) and attempt < max_attempts:
                        # Calcul du backoff exponentiel (0.1, 0.2, 0.4...)
                        delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                        # Ajout de Jitter (variabilité de 0 à 10%) pour désynchroniser les clients
                        jitter = random.uniform(0, delay * 0.1)
                        sleep_time = delay + jitter
                        
                        logger.warning(
                            f"[Retry Policy] Tentative {attempt}/{max_attempts} échouée "
                            f"pour l'opération '{func.__name__}'. Cause: {e}. "
                            f"Nouvel essai dans {sleep_time:.3f}s."
                        )
                        time.sleep(sleep_time)
                    else:
                        # Propager l'exception immédiatement si:
                        # 1. C'est une autre erreur SQLite (ex: syntaxe).
                        # 2. Le nombre max_attempts est atteint.
                        raise e
        return wrapper
    return decorator