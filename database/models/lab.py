from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

if TYPE_CHECKING:
    from database.models.progress import Progress
    from database.models.flag import Flag

class Lab(Base):
    __tablename__ = "labs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    lab_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    lab_progress: Mapped[List["Progress"]] = relationship("Progress", back_populates="lab", cascade="all, delete-orphan")
    flags: Mapped[List["Flag"]] = relationship("Flag", back_populates="lab", cascade="all, delete-orphan")