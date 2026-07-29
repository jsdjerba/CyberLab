from typing import Callable, List, Any, Optional
from application.ports.unit_of_work import AbstractUnitOfWork
from application.ports.event_bus import AbstractEventBus
from infrastructure.repositories.sqlalchemy_lab_repository import SqlAlchemyLabRepository
from infrastructure.repositories.sqlalchemy_student_repository import SqlAlchemyStudentRepository
from infrastructure.repositories.sqlalchemy_lab_instance_repository import SqlAlchemyLabInstanceRepository
from domain.common.aggregate_root import AggregateRoot

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """
    Implémentation concrète de l'Unit of Work pour SQLAlchemy.
    Gère la frontière transactionnelle, un registre explicite d'agrégats,
    et la publication post-commit des Domain Events via l'EventBus.
    """

    def __init__(self, session_factory: Callable[..., Any], event_bus: Optional[AbstractEventBus] = None):
        self._session_factory = session_factory
        self._event_bus = event_bus
        self.session = None
        
        # Registre explicite des agrégats suivis pour cette transaction
        self._registered_aggregates: List[AggregateRoot] = []
        
        # Repositories instanciés sous le même contexte de session
        self.labs = None
        self.students = None
        self.lab_instances = None

    def register_aggregate(self, aggregate: AggregateRoot) -> None:
        """Enregistre explicitement un agrégat pour le suivi des événements."""
        if aggregate not in self._registered_aggregates:
            self._registered_aggregates.append(aggregate)

    def __enter__(self) -> 'SqlAlchemyUnitOfWork':
        self.session = self._session_factory()
        self.labs = SqlAlchemyLabRepository(self.session)
        self.students = SqlAlchemyStudentRepository(self.session)
        self.lab_instances = SqlAlchemyLabInstanceRepository(self.session)
        return super().__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            super().__exit__(exc_type, exc_val, exc_tb)
        finally:
            if self.session:
                self.session.close()

    def commit(self) -> None:
        if self.session:
            self.session.commit()
            
            # Collecte des événements des agrégats enregistrés après commit réussi
            events = self.collect_events()
            
            # Publication via l'EventBus si présent
            if self._event_bus:
                for event in events:
                    self._event_bus.publish(event)

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()
            # En cas de rollback, on purge les événements sans jamais les publier
            for aggregate in self._registered_aggregates:
                aggregate.clear_events()
            self._registered_aggregates.clear()

    def collect_events(self) -> List[Any]:
        events = []
        for aggregate in self._registered_aggregates:
            events.extend(aggregate.collect_events())
        self._registered_aggregates.clear()
        return events