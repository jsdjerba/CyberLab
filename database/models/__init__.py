"""
Registre central des modèles SQLAlchemy.
L'importation de ce module force la métaclasse DeclarativeBase
à inscrire les tables dans Base.metadata.
"""
from database.base import Base
from database.models.enums import UserRole, LabStatus

# Import de la totalité des modèles du domaine
from database.models.user import User
from database.models.lab import Lab
from database.models.progress import Progress
from database.models.classroom import Classroom
from database.models.enrollment import Enrollment
from database.models.user_achievement import UserAchievement
from database.models.flag import Flag  # Ajout critique pour résoudre la relation Lab -> Flag

__all__ = [
    "Base",
    "UserRole",
    "LabStatus",
    "User",
    "Lab",
    "Progress",
    "Classroom",
    "Enrollment",
    "UserAchievement",
    "Flag"
]