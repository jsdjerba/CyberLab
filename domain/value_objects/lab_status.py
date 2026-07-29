from enum import Enum

class LabStatus(str, Enum):
    """
    Value Object (Énumération) représentant l'état strict du cycle de vie d'un laboratoire.
    Hérite de `str` pour garantir la compatibilité native avec la sérialisation (JSON, SQLAlchemy).
    """
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    LOCKED_OUT = "LOCKED_OUT"