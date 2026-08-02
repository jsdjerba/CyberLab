from typing import Callable, Any
from sqlalchemy.orm import Session

class SqlAlchemyUnitOfWork:
    """
    Context Manager gérant l'étanchéité absolue de la transaction.
    Responsable du cycle de vie de la Session (ADR 07.1-2).
    """
    def __init__(self, session_factory: Callable[..., Session]):
        self._session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self):
        self.session = self._session_factory()
        return self

    def commit(self):
        if self.session:
            self.session.commit()

    def rollback(self):
        if self.session:
            self.session.rollback()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if self.session:
            if exc_type is not None:
                self.rollback()
            self.session.close()
            self.session = None