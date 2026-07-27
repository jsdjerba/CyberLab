from typing import Optional, Any
from domain.students.value_objects.student_history import StudentHistory
from domain.labs.value_objects.student_id import StudentId
from database.models.user import User as UserModel
from database.models.progress import Progress as ProgressModel
from database.models.lab import Lab as LabModel

class SqlAlchemyStudentRepository:
    """
    Implémentation SQLAlchemy du repository étudiant.
    Gère la conversion sécurisée entre les modèles ORM et le Value Object StudentHistory du domaine.
    """

    def __init__(self, session: Any):
        self._session = session

    def get_history(self, student_id: StudentId) -> Optional[StudentHistory]:
        # 1. Extraction de la valeur brute de l'identifiant étudiant
        user_id_val = student_id.value if hasattr(student_id, 'value') else int(student_id)

        # 2. Recherche de l'utilisateur ORM correspondant
        user_model = self._session.query(UserModel).filter(
            UserModel.id == user_id_val
        ).first()

        if not user_model:
            return None

        # 3. Récupération des progressions associées avec un statut complété
        # Note : on filtre les entrées dont le statut correspond à une complétion ("COMPLETED")
        progress_models = self._session.query(ProgressModel).filter(
            ProgressModel.user_id == user_id_val,
            ProgressModel.status == "COMPLETED"
        ).all()

        successful_lab_ids = []
        
        # 4. Résolution des identifiants techniques Progress.lab_id vers les identifiants métier Lab.lab_id
        for progress in progress_models:
            lab_model = self._session.query(LabModel).filter(
                LabModel.id == progress.lab_id
            ).first()
            
            if lab_model:
                successful_lab_ids.append(lab_model.lab_id)

        # 5. Construction et retour du Value Object StudentHistory immuable
        # Décision d'architecture pour current_streak : fixée à 0 par défaut en l'absence 
        # d'historique temporel granulaire persisté dans la phase actuelle.
        return StudentHistory(
            completed_lab_count=len(successful_lab_ids),
            successful_lab_ids=tuple(successful_lab_ids),
            current_streak=0
        )