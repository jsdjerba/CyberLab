from typing import List, Optional
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.entities.step import Step
from domain.labs.exceptions import StepNotFound

class Lab:
    """Agrégat représentant la définition statique d'un laboratoire."""
    
    def __init__(
        self,
        id: LabId,
        title: str,
        description: str,
        difficulty: str,
        duration: int,
        steps: List[Step],
        is_published: bool = True,
        required_level: str = "BEGINNER",
        required_lab_ids: Optional[tuple[str, ...]] = None,
        allowed_classrooms: Optional[tuple[str, ...]] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.duration = duration
        self.steps = list(steps)
        self._is_published = is_published
        self._required_level = required_level
        self._required_lab_ids = required_lab_ids or ()
        self._allowed_classrooms = allowed_classrooms

    @property
    def total_points(self) -> int:
        """Calcule le score maximum possible pour ce laboratoire."""
        return sum(step.points for step in self.steps)

    @property
    def is_published(self) -> bool:
        return self._is_published

    @property
    def required_level(self) -> str:
        return self._required_level

    @property
    def required_lab_ids(self) -> tuple[str, ...]:
        return self._required_lab_ids

    @property
    def allowed_classrooms(self) -> Optional[tuple[str, ...]]:
        return self._allowed_classrooms

    def get_steps(self) -> tuple[Step, ...]:
        """Expose les étapes sous forme de collection immuable."""
        return tuple(self.steps)

    def step_count(self) -> int:
        return len(self.steps)

    def contains_step(self, step_id: StepId) -> bool:
        return any(step.id == step_id for step in self.steps)

    def get_step(self, step_id: StepId) -> Step:
        """Récupère une étape ou lève une exception si elle n'existe pas."""
        step = next((step for step in self.steps if step.id == step_id), None)
        if not step:
            raise StepNotFound(f"L'étape {step_id} est introuvable dans ce laboratoire.")
        return step

    def get_available_steps(self, completed_steps: tuple[StepId, ...]) -> tuple[StepId, ...]:
        """
        Détermine les étapes accessibles. 
        Implémentation linéaire actuelle, prête à évoluer vers des graphes/prérequis.
        """
        for step in self.steps:
            if step.id not in completed_steps:
                return (step.id,)
        return ()