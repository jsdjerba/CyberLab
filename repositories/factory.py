from sqlalchemy.orm import Session

# Import Interfaces (Protocols)
from repositories.interfaces.user_repository_interface import IUserRepository
from repositories.interfaces.classroom_repository_interface import IClassroomRepository
from repositories.interfaces.lab_repository_interface import ILabRepository
from repositories.interfaces.progress_repository_interface import IProgressRepository
from repositories.interfaces.achievement_repository_interface import IAchievementRepository
from repositories.interfaces.enrollment_repository_interface import IEnrollmentRepository

# Import Concrete Implementations
from repositories.sqlalchemy.user_repository import UserRepository
from repositories.sqlalchemy.classroom_repository import ClassroomRepository
from repositories.sqlalchemy.lab_repository import LabRepository
from repositories.sqlalchemy.progress_repository import ProgressRepository
from repositories.sqlalchemy.achievement_repository import AchievementRepository
from repositories.sqlalchemy.enrollment_repository import EnrollmentRepository
from repositories.interfaces.health_repository_interface import IHealthRepository


class RepositoryFactory:
    """Centralizes repository instantiation, enforcing interface contracts."""
    def __init__(self, session: Session):
        self._session = session
        self._users = None
        self._classrooms = None
        self._labs = None
        self._progress = None
        self._achievements = None
        self._enrollments = None
        self._health = None

    @property
    def users(self) -> IUserRepository:
        if self._users is None:
            self._users = UserRepository(self._session)
        return self._users

    @property
    def classrooms(self) -> IClassroomRepository:
        if self._classrooms is None:
            self._classrooms = ClassroomRepository(self._session)
        return self._classrooms

    @property
    def labs(self) -> ILabRepository:
        if self._labs is None:
            self._labs = LabRepository(self._session)
        return self._labs

    @property
    def progress(self) -> IProgressRepository:
        if self._progress is None:
            self._progress = ProgressRepository(self._session)
        return self._progress

    @property
    def achievements(self) -> IAchievementRepository:
        if self._achievements is None:
            self._achievements = AchievementRepository(self._session)
        return self._achievements

    @property
    def enrollments(self) -> IEnrollmentRepository:
        if self._enrollments is None:
            self._enrollments = EnrollmentRepository(self._session)
        return self._enrollments
    
    @property
    def health(self) -> IHealthRepository:
        if self._health is None:
            # Concrete implementation injected internally
            from repositories.sqlalchemy.health_repository import HealthRepository
            self._health = HealthRepository(self._session)
        return self._health