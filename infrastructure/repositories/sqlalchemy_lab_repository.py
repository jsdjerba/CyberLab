from typing import Optional, Any
from domain.labs.entities.lab import Lab as DomainLab
from domain.labs.value_objects.lab_id import LabId
from database.models.lab import Lab as LabModel

class SqlAlchemyLabRepository:
    """
    Implémentation SQLAlchemy de LabRepository pour la gestion des laboratoires.
    """

    def __init__(self, session: Any):
        self._session = session

    def get_by_id(self, lab_id: LabId) -> Optional[DomainLab]:
        lab_id_value = lab_id.value if hasattr(lab_id, 'value') else str(lab_id)
        
        lab_model = self._session.query(LabModel).filter(
            LabModel.lab_id == lab_id_value
        ).first()

        if not lab_model:
            return None

        # Instanciation complète de l'entité domaine avec tous ses arguments obligatoires
        return DomainLab(
            id=LabId(lab_model.lab_id),
            title=getattr(lab_model, 'title', ''),
            description=getattr(lab_model, 'description', ''),
            difficulty=getattr(lab_model, 'difficulty', 'Easy'),
            duration=getattr(lab_model, 'duration', 0),
            steps=getattr(lab_model, 'steps', [])
        )