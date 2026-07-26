from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

class Flag(Base):
    __tablename__ = "flags"
    
    __table_args__ = (
        UniqueConstraint("lab_id", "step_id", name="uq_flag_lab_step"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id", ondelete="CASCADE"), nullable=False)
    step_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    flag_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    lab: Mapped["Lab"] = relationship("Lab", back_populates="flags")