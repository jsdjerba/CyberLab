import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base
from database.models.enums import UserRole
from database.types.utc_datetime import UTCDateTime

# Évite les imports circulaires tout en permettant le typage Mapped[]
if TYPE_CHECKING:
    from database.models.classroom import Classroom
    from database.models.enrollment import Enrollment
    from database.models.progress import Progress
    from database.models.user_achievement import UserAchievement

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.STUDENT, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    created_classrooms: Mapped[List["Classroom"]] = relationship(
        "Classroom", back_populates="teacher", cascade="all, delete-orphan"
    )
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", back_populates="user", cascade="all, delete-orphan"
    )
    lab_progress: Mapped[List["Progress"]] = relationship(
        "Progress", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )