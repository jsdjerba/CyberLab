from typing import Optional, Any
from domain.labs.entities.lab import Lab
from domain.labs.value_objects.lab_id import LabId
from database.models.lab import Lab as LabModel

class SqlAlchemyLabRepository:
    """
    Implémentation SQLAlchemy de LabRepository.
    Mappe le modèle ORM Lab vers l'entité Domain Lab.
    """
    def __init__(self, session: Any):
        self._session = session

    def get_by_id(self, lab_id: LabId) -> Optional[Lab]:
        # Recherche par l'identifiant textuel métier 'lab_id' (ex: 'L1')
        target_id = lab_id.value if hasattr(lab_id, 'value') else str(lab_id)
        
        lab_model = self._session.query(LabModel).filter(LabModel.lab_id == target_id).first()
        if not lab_model:
            return None

        # Reconstitution de l'entité Domain Lab selon sa signature réelle exacte
        return Lab(
            id=LabId(lab_model.lab_id),
            title=lab_model.title,
            description=getattr(lab_model, "description", ""), # Sécurisé si la colonne optionnelle
            difficulty=lab_model.difficulty,
            duration=getattr(lab_model, "duration", 0),       # Valeur par défaut si absente du modèle ORM
            steps=[]                                          # Les steps seront gérés/chargés si nécessaire par une relation dédiée
        )