"""
Domain Strategy : Politiques de validation d'un laboratoire.
Définit les conditions de succès (mono-objectif, tous les objectifs, score minimum).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.entities.objective import Objective
from domain.value_objects.objective_id import ObjectiveId


class CompletionPolicy(ABC):
    """Classe de base abstraite pour les stratégies de complétion (Strategy Pattern)."""
    
    @abstractmethod
    def is_complete(self, completed_objectives: list[ObjectiveId], all_objectives: list[Objective]) -> bool:
        pass


@dataclass(frozen=True)
class SingleObjectivePolicy(CompletionPolicy):
    """Condition de succès : Un seul objectif validé suffit."""
    
    def is_complete(self, completed_objectives: list[ObjectiveId], all_objectives: list[Objective]) -> bool:
        return len(completed_objectives) > 0


@dataclass(frozen=True)
class AllObjectivesPolicy(CompletionPolicy):
    """Condition de succès : Tous les objectifs disponibles doivent être validés."""
    
    def is_complete(self, completed_objectives: list[ObjectiveId], all_objectives: list[Objective]) -> bool:
        if not all_objectives:
            return False
        # Utilisation de set pour garantir l'unicité et optimiser la comparaison
        return set(completed_objectives) == set(obj.objective_id for obj in all_objectives)


@dataclass(frozen=True, kw_only=True)
class ScoreBasedPolicy(CompletionPolicy):
    """Condition de succès : Un score cumulé minimum doit être atteint."""
    required_score: int

    def is_complete(self, completed_objectives: list[ObjectiveId], all_objectives: list[Objective]) -> bool:
        current_score = sum(
            obj.score_weight 
            for obj in all_objectives 
            if obj.objective_id in completed_objectives
        )
        return current_score >= self.required_score