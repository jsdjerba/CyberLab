"""
Implémentation SQLAlchemy du repository pour LabInstance.
Gère les opérations de persistance sans aucune contamination de logique métier.
"""

from typing import Optional
from sqlalchemy.orm import Session
from domain.entities.lab_instance import LabInstance
from infrastructure.persistence.models.lab_instance_model import LabInstanceModel
from infrastructure.persistence.mappers.lab_instance_mapper import LabInstanceMapper


class SqlAlchemyLabInstanceRepository:
    """
    Repository concret pour LabInstance basé sur une session SQLAlchemy.
    """

    def __init__(self, session: Session):
        self._session = session

    def _compute_pk(self, student_id: str, lab_id: str) -> str:
        return f"{student_id}#-{lab_id}"

    def save(self, instance: LabInstance) -> None:
        """
        Persiste ou met à jour un Aggregate Root LabInstance dans la base de données.
        """
        pk = self._compute_pk(instance.student_id.value, instance.lab_id.value)
        existing_model = self._session.query(LabInstanceModel).filter_by(id=pk).first()

        model = LabInstanceMapper.to_persistence(instance, existing_model=existing_model)
        
        if not existing_model:
            self._session.add(model)
        
        self._session.flush()

    def find_by_id(self, student_id: str, lab_id: str) -> Optional[LabInstance]:
        """
        Recherche un laboratoire par l'identifiant composite (student_id, lab_id) et le convertit en domaine.
        """
        pk = self._compute_pk(student_id, lab_id)
        model = self._session.query(LabInstanceModel).filter_by(id=pk).first()
        
        if not model:
            return None

        return LabInstanceMapper.to_domain(model)

    def delete(self, student_id: str, lab_id: str) -> None:
        """
        Supprime un enregistrement de laboratoire de la base de données.
        """
        pk = self._compute_pk(student_id, lab_id)
        model = self._session.query(LabInstanceModel).filter_by(id=pk).first()
        if model:
            self._session.delete(model)
            self._session.flush()

    def exists(self, student_id: str, lab_id: str) -> bool:
        """
        Vérifie l'existence d'une instance de laboratoire persistée.
        """
        pk = self._compute_pk(student_id, lab_id)
        count = self._session.query(LabInstanceModel).filter_by(id=pk).count()
        return count > 0