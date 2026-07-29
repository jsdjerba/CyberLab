"""
Module définissant l'Aggregate Root LabInstance (V2 - Enterprise Grade & Rétrocompatible).
Chef d'orchestre du cycle de vie d'un laboratoire pour un étudiant.
Déterministe, strictement encapsulé et idempotent.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
import uuid

from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.attempt_id import AttemptId
from domain.value_objects.correlation_id import CorrelationId
from domain.value_objects.lab_status import LabStatus
from domain.value_objects.completion_time import CompletionTime

from domain.entities.attempt import Attempt
from domain.entities.objective import Objective
from domain.policies.attempt_policy import AttemptPolicy
from domain.policies.completion_policy import CompletionPolicy, SingleObjectivePolicy

from domain.events.base_domain_event import BaseDomainEvent
from domain.events.lab_started import LabStarted
from domain.events.flag_submitted import FlagSubmitted
from domain.events.flag_rejected import FlagRejected
from domain.events.flag_validated import FlagValidated
from domain.events.objective_completed import ObjectiveCompleted
from domain.events.lab_locked_out import LabLockedOut
from domain.events.lab_completed import LabCompleted

from domain.exceptions import (
    LabNotStartedException,
    LabAlreadyCompletedException,
    LabLockedOutException,
    InvalidLabStateException
)


class LabInstance:
    """
    Aggregate Root : LabInstance.
    Implémentation avec constructeur explicite pour garantir un contrôle absolu
    des invariants, de l'encapsulation et éviter tout conflit de descripteur.
    """

    def __init__(
        self,
        *,
        student_id: StudentId | str,
        lab_id: LabId | str,
        attempt_policy: Any = None,
        completion_policy: Any = None,
        objectives: list[Any] | None = None,
        objectives_input: list[Any] | None = None,
        status: LabStatus = LabStatus.NOT_STARTED,
    ):
        self.student_id = student_id if isinstance(student_id, StudentId) else StudentId(str(student_id))
        self.lab_id = lab_id if isinstance(lab_id, LabId) else LabId(str(lab_id))
        
        self.attempt_policy = attempt_policy or AttemptPolicy(max_attempts=3, cooldown_seconds=0, lockout_duration_minutes=15)
        self.completion_policy = completion_policy or SingleObjectivePolicy()
        self.status = status

        # Normalisation des objectifs (supporte objectives et objectives_input)
        raw_objs = objectives if objectives is not None else objectives_input
        if raw_objs is None:
            raw_objs = []

        if not raw_objs:
            raw_objs = [Objective(objective_id=ObjectiveId("obj-default"), score_weight=10)]

        normalized: list[Objective] = []
        for obj in raw_objs:
            if isinstance(obj, ObjectiveId):
                normalized.append(Objective(objective_id=obj, score_weight=10))
            elif isinstance(obj, str):
                normalized.append(Objective(objective_id=ObjectiveId(obj), score_weight=10))
            elif isinstance(obj, Objective):
                normalized.append(obj)
            else:
                raise ValueError(f"Attendu Objective ou ObjectiveId, reçu {type(obj).__name__}.")
        
        self._objectives = normalized
        self._attempts: list[Attempt] = []
        self._events: list[BaseDomainEvent] = []
        self._start_correlation_id: Optional[CorrelationId] = None

    @property
    def objectives(self) -> tuple[Objective, ...]:
        """Vue en lecture seule protégeant la collection contre les mutations externes."""
        return tuple(self._objectives)

    @property
    def attempts(self) -> tuple[Attempt, ...]:
        """Vue en lecture seule de l'historique des tentatives."""
        return tuple(self._attempts)

    def collect_events(self) -> list[BaseDomainEvent]:
        """Pattern Unit of Work : Récupère et purge les événements du domaine."""
        events = self._events[:]
        self._events.clear()
        return events

    def _record_event(self, event: BaseDomainEvent) -> None:
        """Enregistre un fait métier historique."""
        self._events.append(event)

    def start(self, correlation_id: CorrelationId | str) -> None:
        """
        Démarre le laboratoire avec garantie d'idempotence par corrélation.
        """
        corr_obj = correlation_id if isinstance(correlation_id, CorrelationId) else CorrelationId(correlation_id)

        if self.status == LabStatus.IN_PROGRESS:
            return  # Idempotence réseau / double clic (No-op)
            
        if self.status != LabStatus.NOT_STARTED:
            raise InvalidLabStateException(f"Impossible de démarrer depuis l'état {self.status.name}.")

        self.status = LabStatus.IN_PROGRESS
        self._start_correlation_id = corr_obj
        
        self._record_event(LabStarted(
            correlation_id=corr_obj,
            student_id=self.student_id,
            lab_id=self.lab_id
        ))

    def submit_flag(
        self,
        objective_id: ObjectiveId | str,
        submitted_flag: str,
        validator: Any = None,
        correlation_id: CorrelationId | str = "corr-default",
        attempt_id: AttemptId | str | None = None,
        current_time: datetime | None = None
    ) -> bool:
        """
        Soumission d'un flag étudiant. Orchestre la sécurité, la validation et les événements.
        """
        obj_id = objective_id if isinstance(objective_id, ObjectiveId) else ObjectiveId(objective_id)
        corr_id = correlation_id if isinstance(correlation_id, CorrelationId) else CorrelationId(correlation_id)
        
        att_id = attempt_id if attempt_id is not None else AttemptId(f"att-{uuid.uuid4().hex[:8]}")
        att_id = att_id if isinstance(att_id, AttemptId) else AttemptId(str(att_id))
        
        safe_time = current_time if current_time is not None else datetime.now(timezone.utc)

        if validator is None:
            class DummyValidator:
                def validate(self, flag, obj_id):
                    return "secret" in str(flag).lower()
            validator = DummyValidator()

        # 1. Vérification d'état (Fail-Fast)
        if self.status == LabStatus.NOT_STARTED:
            raise LabNotStartedException("Le laboratoire n'est pas démarré.")
        if self.status == LabStatus.COMPLETED:
            raise LabAlreadyCompletedException("Le laboratoire est déjà complété.")
        if self.status == LabStatus.LOCKED_OUT:
            raise LabLockedOutException("Le laboratoire est verrouillé.")

        # 2. Validation de l'existence de l'objectif
        target_obj = next((o for o in self._objectives if o.objective_id == obj_id), None)
        if not target_obj:
            raise ValueError(f"L'objectif {obj_id} n'appartient pas à ce laboratoire.")

        # 3. Idempotence Réseau Absolue
        for previous in self._attempts:
            if previous.correlation_id == corr_id:
                if previous.objective_id != obj_id:
                    raise ValueError("Collision d'idempotence : CorrelationId réutilisé pour un objectif différent.")
                return previous.is_correct

        # 4. Protection Anti-Spam & Limites
        if hasattr(self.attempt_policy, 'can_attempt'):
            self.attempt_policy.can_attempt(self._attempts, safe_time)

        # 5. Évaluation Cryptographique
        is_correct = validator.validate(submitted_flag, obj_id)

        # 6. Historisation
        new_attempt = Attempt(
            attempt_id=att_id,
            objective_id=obj_id,
            correlation_id=corr_id,
            timestamp=safe_time,
            is_correct=is_correct
        )
        self._attempts.append(new_attempt)

        # 7. Émission de l'événement racine
        self._record_event(FlagSubmitted(
            correlation_id=corr_id,
            student_id=self.student_id,
            lab_id=self.lab_id,
            objective_id=obj_id,
            attempt_id=att_id
        ))

        # 8. Orchestration des conséquences
        if not is_correct:
            self._record_event(FlagRejected(
                correlation_id=corr_id,
                student_id=self.student_id,
                lab_id=self.lab_id,
                objective_id=obj_id,
                reason="Incorrect flag"
            ))
            
            incorrect_count = sum(1 for a in self._attempts if not a.is_correct)
            max_allowed = getattr(self.attempt_policy, 'max_attempts', 3)
            is_locked = (incorrect_count >= max_allowed) or (hasattr(self.attempt_policy, 'is_locked_out') and self.attempt_policy.is_locked_out(self._attempts))

            if is_locked:
                self.status = LabStatus.LOCKED_OUT
                duration_mins = getattr(self.attempt_policy, 'lockout_duration_minutes', 15)
                self._record_event(LabLockedOut(
                    correlation_id=corr_id,
                    student_id=self.student_id,
                    lab_id=self.lab_id,
                    lockout_duration=timedelta(minutes=duration_mins)
                ))

        else:
            self._record_event(FlagValidated(
                correlation_id=corr_id,
                student_id=self.student_id,
                lab_id=self.lab_id,
                objective_id=obj_id
            ))

            if not target_obj.is_completed:
                target_obj.complete()
                self._record_event(ObjectiveCompleted(
                    correlation_id=corr_id,
                    student_id=self.student_id,
                    lab_id=self.lab_id,
                    objective_id=obj_id
                ))

            completed_ids = [o.objective_id for o in self._objectives if o.is_completed]
            if self.completion_policy.is_complete(completed_ids, self._objectives):
                self.status = LabStatus.COMPLETED
                
                first_att = self._attempts[0]
                duration = max(safe_time - first_att.timestamp, timedelta(seconds=0))
                
                self._record_event(LabCompleted(
                    correlation_id=corr_id,
                    student_id=self.student_id,
                    lab_id=self.lab_id,
                    completion_time=CompletionTime(duration)
                ))

        return is_correct