"""
Module définissant l'entité interne Attempt.
Représente un fait historique immuable lié à une soumission dans le Learning Context.
"""

from dataclasses import dataclass
from datetime import datetime

from domain.value_objects.attempt_id import AttemptId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.correlation_id import CorrelationId


@dataclass(frozen=True, kw_only=True, slots=True, eq=False)
class Attempt:
    """
    Entité interne (Child Entity) de l'Aggregate Root LabInstance.
    Trace une tentative effectuée par un étudiant.
    
    L'utilisation de `slots=True` et `frozen=True` interdit l'ajout d'attributs dynamiques
    (comme `plaintext_flag`) à l'exécution.
    L'attribut `eq=False` garantit que l'égalité sera calculée sur l'identité (DDD Entity).
    """
    attempt_id: AttemptId
    objective_id: ObjectiveId
    correlation_id: CorrelationId
    timestamp: datetime
    is_correct: bool

    def __post_init__(self) -> None:
        """
        Validation stricte des invariants : Anti-Primitive Obsession et Cohérence Temporelle.
        """
        if not isinstance(self.attempt_id, AttemptId):
            raise ValueError("attempt_id doit être une instance stricte de AttemptId.")
            
        if not isinstance(self.objective_id, ObjectiveId):
            raise ValueError("objective_id doit être une instance stricte de ObjectiveId.")
            
        if not isinstance(self.correlation_id, CorrelationId):
            raise ValueError("correlation_id doit être une instance stricte de CorrelationId.")
            
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp doit être une instance stricte de datetime.")
            
        # Protection contre l'instabilité temporelle : interdit les dates ambiguës.
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp doit être timezone-aware (UTC recommandé).")
            
        if type(self.is_correct) is not bool:
            raise ValueError("is_correct doit être un booléen strict (True ou False).")

    def __eq__(self, other: object) -> bool:
        """
        Respect du contrat DDD Entity :
        L'égalité structurelle est interdite. Deux tentatives sont considérées égales
        si et seulement si elles partagent le même identifiant métier (AttemptId).
        """
        if not isinstance(other, Attempt):
            return NotImplemented
        return self.attempt_id == other.attempt_id

    def __hash__(self) -> int:
        """
        Permet l'utilisation de l'entité dans des ensembles (sets) ou comme clé,
        basée exclusivement sur son identité immuable.
        """
        return hash(self.attempt_id)