"""
Schéma de validation et DTO pour la soumission de flag (Presentation DTOs).
Assure la validation stricte des charges utiles HTTP entrantes.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SubmitFlagRequestDTO:
    objective_id: str
    flag: str
    correlation_id: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "SubmitFlagRequestDTO":
        if not data or not isinstance(data, dict):
            raise ValueError("Payload JSON invalide.")
        
        objective_id = data.get("objective_id")
        flag = data.get("flag")
        correlation_id = data.get("correlation_id")

        if not objective_id or not isinstance(objective_id, str):
            raise ValueError("Le champ 'objective_id' est obligatoire et doit être une chaîne.")
        if not flag or not isinstance(flag, str):
            raise ValueError("Le champ 'flag' est obligatoire et doit être une chaîne.")

        return SubmitFlagRequestDTO(
            objective_id=objective_id.strip(),
            flag=flag.strip(),
            correlation_id=str(correlation_id) if correlation_id else None
        )