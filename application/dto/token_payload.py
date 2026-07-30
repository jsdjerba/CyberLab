"""DTO pour le transfert sécurisé des données du token vers la couche présentation."""
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class TokenPayload:
    user_id: str
    role: str
    issued_at: datetime
    expiration: datetime
    # Ce champ est crucial pour le SecurityService (Phase 5.5 Enterprise)
    claims: dict = field(default_factory=dict)