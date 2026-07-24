from typing import Optional
from sqlalchemy.orm import Session
from application.labs.interfaces.lab_instance_repository import LabInstanceRepository
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from infrastructure.database.models.lab_instance_model import LabInstanceModel
from infrastructure.database.models.step_attempt_model import StepAttemptModel
from infrastructure.mappers.lab_instance_mapper import LabInstanceMapper

class SqlAlchemyLabInstanceRepository(LabInstanceRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_student_and_lab(self, student_id: StudentId, lab_id: LabId) -> Optional[LabInstance]:
        model = self.session.query(LabInstanceModel).filter_by(
            student_id=student_id.value, 
            lab_id=lab_id.value
        ).first()
        
        if not model:
            return None
            
        return LabInstanceMapper.to_domain(model)

    def save(self, instance: LabInstance) -> None:
        model_to_save = LabInstanceMapper.to_model(instance)
        
        existing = self.session.query(LabInstanceModel).filter_by(id=instance.id).first()
        
        if existing:
            # Update explicit
            existing.status = model_to_save.status
            existing.current_step = model_to_save.current_step
            existing.score = model_to_save.score
            existing.completed_steps = model_to_save.completed_steps
            
            # Gestion de la sous-collection (attempts)
            existing_attempts_map = {a.step_id: a for a in existing.attempts}
            
            for step_id, count in instance.attempts.items():
                if step_id in existing_attempts_map:
                    existing_attempts_map[step_id].attempt_count = count
                else:
                    existing.attempts.append(StepAttemptModel(step_id=step_id, attempt_count=count))
        else:
            # Insertion initiale
            self.session.add(model_to_save)