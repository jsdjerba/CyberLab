from dataclasses import dataclass
from domain.events.base_domain_event import BaseDomainEvent

@dataclass(frozen=True, kw_only=True)
class ScoreUpdated(BaseDomainEvent):
    """
    Fait passé immuable : Le score d'un étudiant a été mis à jour avec succès.
    """
    student_id: str
    added_points: int
    new_total_score: int