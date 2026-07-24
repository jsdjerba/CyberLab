import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

if TYPE_CHECKING:
    from database.models.user import User
    from database.models.enrollment import Enrollment

class Classroom(Base):
    __tablename__ = "classrooms"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    teacher: Mapped["User"] = relationship("User", back_populates="created_classrooms")
    enrollments: Mapped[List["Enrollment"]] = relationship("Enrollment", back_populates="classroom", cascade="all, delete-orphan")