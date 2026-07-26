from typing import Optional, Any
from datetime import datetime
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.lab_status import LabStatus
from database.models.progress import Progress as ProgressModel
from database.models.lab import Lab as LabModel

class SqlAlchemyLabInstanceRepository:
    """
    Implémentation SQLAlchemy de LabInstanceRepository respectant la Clean Architecture.
    Gère la persistance et le mapping bidirectionnel ORM ↔ Domaine.
    """

    def __init__(self, session: Any):
        self._session = session

    def get_by_id(self, instance_id: str) -> Optional[LabInstance]:
        # 1. Recherche de l'enregistrement Progress par son domain_id
        progress_model = self._session.query(ProgressModel).filter(
            ProgressModel.domain_id == instance_id
        ).first()
        
        if not progress_model:
            return None

        # 2. Résolution du lab_id métier via la clé technique stockée dans Progress.lab_id
        lab_model = self._session.query(LabModel).filter(
            LabModel.id == progress_model.lab_id
        ).first()
        
        if not lab_model:
            return None

        lab_id_obj = LabId(lab_model.lab_id)
        student_id_obj = StudentId(progress_model.user_id)
        
        # 3. Conversion sécurisée du statut
        status_enum = LabStatus(progress_model.status) if isinstance(progress_model.status, str) else progress_model.status

        # 4. Instanciation/Reconstruction de l'agrégat via le constructeur standard
        instance = LabInstance(progress_model.domain_id, student_id_obj, lab_id_obj)
        instance.status = status_enum
        instance.started_at = progress_model.started_at
        instance.completed_at = progress_model.completed_at
        
        return instance

    def get_by_student_and_lab(self, student_id: StudentId, lab_id: LabId) -> Optional[LabInstance]:
        student_id_val = student_id.value if hasattr(student_id, 'value') else int(student_id)
        lab_id_val = lab_id.value if hasattr(lab_id, 'value') else str(lab_id)

        lab_model = self._session.query(LabModel).filter(
            LabModel.lab_id == lab_id_val
        ).first()

        if not lab_model:
            return None

        progress_model = self._session.query(ProgressModel).filter(
            ProgressModel.user_id == student_id_val,
            ProgressModel.lab_id == lab_model.id
        ).first()

        if not progress_model:
            return None

        return self.get_by_id(progress_model.domain_id)

    def save(self, instance: LabInstance) -> None:
        # 1. Extraction et résolution de la clé technique LabModel.id à partir du LabId métier
        lab_id_value = instance.lab_id.value if hasattr(instance.lab_id, 'value') else str(instance.lab_id)
        lab_model = self._session.query(LabModel).filter(
            LabModel.lab_id == lab_id_value
        ).first()
        
        if not lab_model:
            raise ValueError(f"Lab with business id '{lab_id_value}' not found in database.")

        student_id_value = instance.student_id.value if hasattr(instance.student_id, 'value') else int(instance.student_id)
        instance_id_value = instance.id.value if hasattr(instance.id, 'value') else str(instance.id)
        status_value = instance.status.value if hasattr(instance.status, 'value') else str(instance.status)

        # 2. Recherche d'un enregistrement Progress existant
        progress_model = self._session.query(ProgressModel).filter(
            ProgressModel.domain_id == instance_id_value
        ).first()

        if progress_model:
            # Mise à jour des champs modifiables
            progress_model.user_id = student_id_value
            progress_model.lab_id = lab_model.id
            progress_model.status = status_value
            progress_model.started_at = getattr(instance, 'started_at', progress_model.started_at)
            progress_model.completed_at = getattr(instance, 'completed_at', progress_model.completed_at)
        else:
            # Création d'un nouvel enregistrement Progress
            progress_model = ProgressModel(
                domain_id=instance_id_value,
                user_id=student_id_value,
                lab_id=lab_model.id,
                status=status_value,
                started_at=getattr(instance, 'started_at', datetime.utcnow()),
                completed_at=getattr(instance, 'completed_at', None)
            )
            self._session.add(progress_model)

        self._session.flush()