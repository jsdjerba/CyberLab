"""
Implémentation SQLAlchemy de l'Unit of Work (Infrastructure).
"""

from sqlalchemy.orm import Session


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session):
        self._session = session
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            self.rollback()
        elif not self.committed:
            self.commit()
        self._session.close()

    def commit(self) -> None:
        self._session.commit()
        self.committed = True
        self.rolled_back = False

    def rollback(self) -> None:
        self._session.rollback()
        self.rolled_back = True
        self.committed = False