from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.base import Base

class StepAttemptModel(Base):
    __tablename__ = "step_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lab_instance_id: Mapped[str] = mapped_column(ForeignKey("lab_instances.id", ondelete="CASCADE"))
    step_id: Mapped[str] = mapped_column(String, nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relation bidirectionnelle explicite
    lab_instance: Mapped["LabInstanceModel"] = relationship(back_populates="attempts")