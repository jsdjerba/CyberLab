from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True, kw_only=True)
class BaseDomainEvent:
    """
    Classe parente abstraite pour tous les événements du domaine.
    Garantit l'immuabilité et la présence des métadonnées techniques.
    Le correlation_id doit être fourni par le Use Case (couche Application).
    """
    correlation_id: str
    # Génération automatique du timestamp UTC à la création de l'événement
    timestamp: datetime = field(default_factory=datetime.utcnow)