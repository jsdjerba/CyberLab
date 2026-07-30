"""
Modèles SQLAlchemy pour la persistance des instances de laboratoire (Phase 3.2).
Stricquement découplés du domaine : aucune logique métier, uniquement du mapping tabulaire.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from infrastructure.database import Base
from domain.value_objects.lab_status import LabStatus


class LabInstanceModel(Base):
    __tablename__ = "lab_instances"

    id = Column(String(255), primary_key=True)  # Clé technique composite (student_id#lab_id)
    student_id = Column(String(255), nullable=False, index=True)
    lab_id = Column(String(255), nullable=False, index=True)
    status = Column(Enum(LabStatus), nullable=False, default=LabStatus.NOT_STARTED)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relations ORM avec cascade de suppression
    objectives = relationship("ObjectiveModel", back_populates="lab_instance", cascade="all, delete-orphan", passive_deletes=True)
    attempts = relationship("AttemptModel", back_populates="lab_instance", cascade="all, delete-orphan", passive_deletes=True)


class ObjectiveModel(Base):
    __tablename__ = "lab_objectives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lab_instance_id = Column(String(255), ForeignKey("lab_instances.id", ondelete="CASCADE"), nullable=False)
    objective_id = Column(String(255), nullable=False)
    score_weight = Column(Integer, nullable=False, default=10)
    is_completed = Column(Boolean, nullable=False, default=False)

    lab_instance = relationship("LabInstanceModel", back_populates="objectives")


class AttemptModel(Base):
    __tablename__ = "lab_attempts"

    id = Column(String(255), primary_key=True)
    lab_instance_id = Column(String(255), ForeignKey("lab_instances.id", ondelete="CASCADE"), nullable=False)
    objective_id = Column(String(255), nullable=False)
    correlation_id = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    is_correct = Column(Boolean, nullable=False)

    lab_instance = relationship("LabInstanceModel", back_populates="attempts")