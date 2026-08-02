# infrastructure/persistence/sqlite/models.py
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TeamModel(Base):
    __tablename__ = 'teams'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    classroom_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)
    
    # CORRECTION : server_default force l'écriture du DEFAULT 0 dans le DDL SQL
    score: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    
    max_size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint('score >= 0', name='check_team_score_positive'),
    )

class TeamMemberModel(Base):
    # ... (Le reste du fichier reste identique)
    __tablename__ = 'team_members'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    team_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("teams.id", ondelete="CASCADE"), 
        nullable=False
    )
    student_id: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint('team_id', 'student_id', name='uq_team_student'),
    )