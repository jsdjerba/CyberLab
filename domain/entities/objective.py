"""
Module définissant l'entité interne Objective.
Représente une cible pédagogique au sein d'un laboratoire.
"""

from dataclasses import dataclass

from domain.value_objects.objective_id import ObjectiveId


@dataclass(slots=True, kw_only=True, eq=False)
class Objective:
    """
    Entité interne (Child Entity) de LabInstance.
    Représente un objectif spécifique (ex: trouver un port ouvert).
    
    L'utilisation de `slots=True` garantit une faible empreinte mémoire
    et empêche l'ajout d'attributs dynamiques imprévus (Anti-Leak).
    La mutabilité est autorisée mais strictement encapsulée.
    """
    objective_id: ObjectiveId
    score_weight: int
    is_completed: bool = False

    def __post_init__(self) -> None:
        """
        Validation stricte des invariants métier à l'instanciation.
        """
        if not isinstance(self.objective_id, ObjectiveId):
            raise ValueError("objective_id doit être une instance stricte de ObjectiveId.")
            
        # type() strict car bool hérite de int en Python (isinstance(True, int) == True)
        if type(self.score_weight) is not int:
            raise ValueError("score_weight doit être un entier strict.")
            
        if self.score_weight < 0:
            raise ValueError("score_weight ne peut pas être négatif.")
            
        if type(self.is_completed) is not bool:
            raise ValueError("is_completed doit être un booléen strict.")

    def complete(self) -> None:
        """
        Transition d'état métier explicite (Tell, Don't Ask).
        La méthode est idempotente : la rappeler n'a aucun effet secondaire nocif.
        """
        self.is_completed = True

    def __eq__(self, other: object) -> bool:
        """
        Respect du contrat DDD Entity :
        L'égalité est dictée uniquement par l'identité (ObjectiveId), 
        indépendamment de l'état d'achèvement ou du score.
        """
        if not isinstance(other, Objective):
            return NotImplemented
        return self.objective_id == other.objective_id

    def __hash__(self) -> int:
        """
        Le hash repose exclusivement sur l'identité immuable.
        """
        return hash(self.objective_id)