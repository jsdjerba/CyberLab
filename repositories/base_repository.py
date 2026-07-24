from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    def get_by_id(self, record_id: int) -> Optional[T]:
        return self.session.get(self.model_class, record_id)

    def get_all(self) -> List[T]:
        stmt = select(self.model_class)
        return list(self.session.scalars(stmt).all())

    def create(self, entity: T) -> T:
        self.session.add(entity)
        self.session.flush() # Send to DB, but wait for UnitOfWork to commit
        return entity

    def delete(self, entity: T) -> None:
        self.session.delete(entity)
        self.session.flush()