from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base
from database.models.enums import LabStatus

class Progress(Base):
    # Conservation de la compatibilité SQL stricte
    __tablename__ = "lab_progress"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id", ondelete="CASCADE"), index=True, nullable=False)
    
    status: Mapped[LabStatus] = mapped_column(default=LabStatus.NOT_STARTED, nullable=False)
    started_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)

    # Note : user doit avoir la référence inverse vers la propriété définie dans le modèle User
    user: Mapped["User"] = relationship("User", back_populates="lab_progress") 
    lab: Mapped["Lab"] = relationship("Lab", back_populates="lab_progress")