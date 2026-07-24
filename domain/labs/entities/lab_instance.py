from datetime import datetime
from typing import Optional, List, Dict, Any
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.lab_status import LabStatus
from domain.labs.exceptions import InvalidLabState, InvalidStepTransition, StepAlreadyCompleted, StepNotFound
from domain.labs.events.lab_started import LabStarted
from domain.labs.events.step_completed import StepCompleted
from domain.labs.events.lab_finished import LabFinished

class LabInstance:
    """Agrégat représentant l'instance d'exécution d'un laboratoire par un étudiant."""

    def __init__(
        self,
        id: str,
        student_id: StudentId,
        lab_id: LabId,
        status: LabStatus = LabStatus.NOT_STARTED,
        current_step: Optional[StepId] = None,
        completed_steps: Optional[List[StepId]] = None,
        attempts: Optional[Dict[Any, int]] = None,
        last_attempt_times: Optional[Dict[str, datetime]] = None,
        score: int = 0
    ):
        self._id = id
        self._student_id = student_id
        self._lab_id = lab_id
        self._status = status
        self._current_step = current_step
        self._completed_steps = list(completed_steps) if completed_steps else []
        
        self._attempts_count = {
            (k.value if hasattr(k, 'value') else str(k)): v 
            for k, v in (attempts or {}).items()
        }
        
        self._last_attempt_times: Dict[str, datetime] = dict(last_attempt_times) if last_attempt_times else {}
        self._events: List[Any] = []
        self._score = score

    @property
    def id(self) -> str:
        return self._id

    @property
    def student_id(self) -> StudentId:
        return self._student_id

    @property
    def lab_id(self) -> LabId:
        return self._lab_id

    @property
    def status(self) -> LabStatus:
        return self._status

    @status.setter
    def status(self, new_status: LabStatus) -> None:
        self._status = new_status

    @property
    def current_step(self) -> Optional[StepId]:
        return self._current_step

    @current_step.setter
    def current_step(self, step: Optional[StepId]) -> None:
        self._current_step = step

    @property
    def completed_steps(self) -> tuple[StepId, ...]:
        return tuple(self._completed_steps)

    @completed_steps.setter
    def completed_steps(self, steps: List[StepId]) -> None:
        self._completed_steps = list(steps)

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        self._score = value

    @property
    def attempts(self) -> Dict[str, int]:
        return dict(self._attempts_count)

    @attempts.setter
    def attempts(self, attempts_dict: Dict[Any, int]) -> None:
        self._attempts_count = {
            (k.value if hasattr(k, 'value') else str(k)): v 
            for k, v in attempts_dict.items()
        }

    # --- NOUVELLES MÉTHODES D'ENCAPSULATION POUR LE PROGRESS SERVICE ---
    
    def get_completed_steps(self) -> tuple[StepId, ...]:
        """Retourne une copie immuable des étapes complétées."""
        return tuple(self._completed_steps)

    def is_step_completed(self, step_id: StepId) -> bool:
        return step_id in self._completed_steps

    def completed_steps_count(self) -> int:
        return len(self._completed_steps)

    # -------------------------------------------------------------------

    def get_attempt_count(self, step_id: StepId) -> int:
        key = step_id.value if hasattr(step_id, 'value') else str(step_id)
        return self._attempts_count.get(key, 0)

    def get_last_attempt_time(self, step_id: StepId) -> Optional[datetime]:
        key = step_id.value if hasattr(step_id, 'value') else str(step_id)
        return self._last_attempt_times.get(key)

    def record_attempt(self, step_id: StepId, timestamp: datetime) -> None:
        key = step_id.value if hasattr(step_id, 'value') else str(step_id)
        self._attempts_count[key] = self._attempts_count.get(key, 0) + 1
        self._last_attempt_times[key] = timestamp

    def start_lab(self, lab: Any) -> None:
        if self._status != LabStatus.NOT_STARTED:
            raise InvalidLabState("Le laboratoire est déjà démarré ou terminé.")
        if not lab.steps:
            raise InvalidLabState("Un laboratoire vide ne peut pas être démarré.")
        
        self._status = LabStatus.IN_PROGRESS
        self._current_step = lab.steps[0].id

        try:
            event = LabStarted(self._id)
        except TypeError:
            event = LabStarted(self._id, self._lab_id, self._student_id)
            
        self._events.append(event)

    def pause(self) -> None:
        if self._status != LabStatus.IN_PROGRESS:
            raise InvalidLabState("Impossible de mettre en pause un laboratoire non en cours.")
        self._status = LabStatus.PAUSED

    def abandon(self) -> None:
        if self._status not in {LabStatus.IN_PROGRESS, LabStatus.PAUSED}:
            raise InvalidLabState("Impossible d'abandonner ce laboratoire dans cet état.")
        self._status = LabStatus.ABANDONED

    def complete(self) -> None:
        if self._status != LabStatus.IN_PROGRESS:
            raise InvalidLabState("Le laboratoire doit être en cours pour être complété.")
        self._status = LabStatus.COMPLETED

    def complete_step(self, step_id: StepId, lab: Any) -> None:
        if self._status != LabStatus.IN_PROGRESS:
            raise InvalidLabState("IN_PROGRESS : Le laboratoire n'est pas en cours d'exécution.")
        
        if step_id in self._completed_steps:
            raise StepAlreadyCompleted(f"L'étape {step_id} est déjà validée.")

        if self._current_step != step_id:
            raise InvalidStepTransition(f"Impossible de valider l'étape, attendu: {self._current_step}")

        step = next((s for s in lab.steps if s.id == step_id), None)
        if not step:
            raise StepNotFound("L'étape n'existe pas dans le laboratoire.")

        self._completed_steps.append(step_id)
        self._score += step.points
        
        step_str = step_id.value if hasattr(step_id, 'value') else str(step_id)

        self._events.append(StepCompleted(
            lab_instance_id=self._id, 
            step_id=step_str, 
            score_awarded=step.points
        ))

        current_index = lab.steps.index(step)
        if current_index + 1 >= len(lab.steps):
            self.complete()
            self._current_step = None
            self._events.append(LabFinished(
                lab_instance_id=self._id, 
                final_score=self._score
            ))
        else:
            self._current_step = lab.steps[current_index + 1].id

    def pull_events(self) -> List[Any]:
        events = list(self._events)
        self._events.clear()
        return events

    @classmethod
    def reconstitute(
        cls, 
        id: str, 
        student_id: StudentId, 
        lab_id: LabId, 
        status: LabStatus, 
        current_step: Optional[StepId], 
        completed_steps: List[StepId], 
        attempts: Dict[str, int], 
        score: int = 0
    ) -> 'LabInstance':
        return cls(
            id=id,
            student_id=student_id,
            lab_id=lab_id,
            status=status,
            current_step=current_step,
            completed_steps=completed_steps,
            attempts=attempts,
            score=score
        )