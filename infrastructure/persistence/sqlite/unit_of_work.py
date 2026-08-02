from sqlalchemy.orm import sessionmaker
from infrastructure.persistence.sqlite.team_repository import SqlAlchemyTeamRepository
from infrastructure.persistence.sqlite.outbox_repository import SqlAlchemyOutboxRepository

class SqlAlchemyUnitOfWork:
    """
    Unit of Work SQLAlchemy gérant la frontière transactionnelle unique
    pour l'état métier (Teams) et l'Outbox (Domain Events).
    """
    def __init__(self, engine):
        self._session_maker = sessionmaker(bind=engine)
        self.session = None
        self.teams = None
        self.outbox = None

    def __enter__(self):
        self.session = self._session_maker()
        self.teams = SqlAlchemyTeamRepository(self.session)
        self.outbox = SqlAlchemyOutboxRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        self.session.close()

    def commit(self):
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def rollback(self):
        self.session.rollback()