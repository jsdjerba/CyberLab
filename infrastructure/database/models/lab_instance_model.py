from sqlalchemy import String, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from infrastructure.database.base import Base
# Note: utiliser des chaînes pour éviter les imports circulaires dans DeclarativeBase
from infrastructure.database.models.step_attempt_model import StepAttemptModel

class LabInstanceModel(Base):
    __tablename__ = "lab_instances"
    
    # Contrainte : Un étudiant ne peut avoir qu'une seule instance par lab
    __table_args__ = (
        UniqueConstraint('student_id', 'lab_id', name='uq_student_lab'),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, nullable=False)
    lab_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    current_step: Mapped[str] = mapped_column(String, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_steps: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # back_populates et cascade delete
    attempts: Mapped[List["StepAttemptModel"]] = relationship(
        back_populates="lab_instance", 
        cascade="all, delete-orphan"
    )