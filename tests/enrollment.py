from database.unit_of_work import UnitOfWork
from repositories.sqlalchemy.user_repository import UserRepository
from repositories.sqlalchemy.achievement_repository import AchievementRepository
from database.models import User, Achievement

def test_atomic_transaction_with_multiple_repos(db_session):
    user_repo = UserRepository(db_session)
    achieve_repo = AchievementRepository(db_session)
    
    try:
        with UnitOfWork(db_session) as uow:
            u1 = user_repo.create_user(User(username="atomic", password_hash="h"))
            a1 = achieve_repo.create(Achievement(name="Badge", description="D", icon="I"))
            # Provocation d'une erreur métier
            raise ValueError("Erreur critique")
    except ValueError:
        pass
        
    assert user_repo.get_by_username("atomic") is None
    assert db_session.query(Achievement).count() == 0