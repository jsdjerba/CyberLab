from typing import Set
from domain.common.aggregate_root import AggregateRoot
from domain.value_objects.completed_lab_id import CompletedLabId
from domain.events.score_updated import ScoreUpdated

class StudentProfile(AggregateRoot):
    """
    Aggregate Root représentant le profil d'un étudiant (Gamification).
    Garantit l'idempotence des attributions de score (un lab = une récompense).
    """
    def __init__(self, student_id: str, total_score: int = 0):
        super().__init__()
        if total_score < 0:
            raise ValueError("Le score total ne peut pas être négatif à l'initialisation.")
            
        self.student_id = student_id
        self.total_score = total_score
        
        # Collection interne garantissant l'unicité des labs scorés
        self._completed_labs: Set[CompletedLabId] = set()

    def add_score_for_lab(self, lab_id: str, score: int, correlation_id: str) -> None:
        """
        Ajoute un score si le lab n'a pas déjà été comptabilisé (Idempotence).
        """
        # 1. Vérification de l'invariant de score
        if self.total_score + score < 0:
            raise ValueError("Le score total ne peut pas être négatif.")

        # 2. Encapsulation dans un Value Object
        completed_lab = CompletedLabId(lab_id)

        # 3. Vérification de l'idempotence
        if completed_lab in self._completed_labs:
            return  # Ignoré silencieusement : pas de modification, pas d'événement

        # 4. Modification de l'état
        self._completed_labs.add(completed_lab)
        self.total_score += score

        # 5. Enregistrement de l'événement métier
        self.register_event(
            ScoreUpdated(
                correlation_id=correlation_id,
                student_id=self.student_id,
                added_points=score,
                new_total_score=self.total_score
            )
        )