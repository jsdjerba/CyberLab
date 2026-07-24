from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.lab_status import LabStatus
from infrastructure.database.models.lab_instance_model import LabInstanceModel
from infrastructure.database.models.step_attempt_model import StepAttemptModel

class LabInstanceMapper:
    @staticmethod
    def to_domain(model: LabInstanceModel) -> LabInstance:
        """SQLAlchemy Model -> Domain Entity"""
        return LabInstance.reconstitute(
            id=str(model.id),
            student_id=StudentId(model.student_id),
            lab_id=LabId(model.lab_id),
            status=LabStatus(model.status),
            score=model.score,
            current_step=StepId(model.current_step) if model.current_step else None,
            completed_steps=[
                StepId(s) if isinstance(s, str) else s 
                for s in model.completed_steps
            ],
            attempts={
                StepId(a.step_id) if isinstance(a.step_id, str) else a.step_id: a.attempt_count 
                for a in model.attempts
            }
        )

    @staticmethod
    def to_model(entity: LabInstance) -> LabInstanceModel:
        """Domain Entity -> SQLAlchemy Model"""
        attempts_models = [
            StepAttemptModel(
                step_id=sid.value if hasattr(sid, 'value') else str(sid), 
                attempt_count=cnt
            )
            for sid, cnt in entity.attempts.items()
        ]
        
        return LabInstanceModel(
            id=entity.id,
            student_id=entity.student_id.value,
            lab_id=entity.lab_id.value,
            status=entity.status.value,
            current_step=entity.current_step.value if entity.current_step else None,
            score=entity.score,
            completed_steps=[
                s.value if hasattr(s, 'value') else str(s) 
                for s in entity.completed_steps
            ],
            attempts=attempts_models
        )