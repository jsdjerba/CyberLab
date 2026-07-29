"""
Événement de domaine : FlagValidated.
"""

from dataclasses import dataclass
from domain.events.base_domain_event import BaseDomainEvent
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId


@dataclass(frozen=True, kw_only=True)
class FlagValidated(BaseDomainEvent):
    student_id: StudentId | str
    lab_id: LabId | str
    objective_id: ObjectiveId | str = "obj-default"
    attempt_number: int | None = None