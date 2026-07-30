"""
Mapper bidirectionnel (Anti-Corruption Layer) entre l'Aggregate Root LabInstance et les modèles SQLAlchemy.
Garantit la réhydratation intègre des Value Objects et la normalisation des types d'infrastructure (ex: Timezones).
"""

from datetime import timezone
from domain.entities.lab_instance import LabInstance
from domain.entities.objective import Objective
from domain.entities.attempt import Attempt
from domain.value_objects.student_id import StudentId
from domain.value_objects.lab_id import LabId
from domain.value_objects.objective_id import ObjectiveId
from domain.value_objects.attempt_id import AttemptId
from domain.value_objects.correlation_id import CorrelationId
from infrastructure.persistence.models.lab_instance_model import LabInstanceModel, ObjectiveModel, AttemptModel


class LabInstanceMapper:
    """
    Traducteur agissant comme un adaptateur entre le monde relationnel ORM et le domaine pur.
    """

    @staticmethod
    def to_domain(model: LabInstanceModel) -> LabInstance:
        """
        Transforme un modèle SQLAlchemy persistant en Aggregate Root LabInstance.
        Normalise les datetimes naïfs issus de SQLite en datetimes timezone-aware UTC.
        """
        if not model:
            return None

        # 1. Reconstruction des objets Objective du domaine
        objectives = [
            Objective(
                objective_id=ObjectiveId(obj_model.objective_id),
                score_weight=obj_model.score_weight,
                is_completed=obj_model.is_completed
            )
            for obj_model in model.objectives
        ]

        # 2. Instanciation de l'agrégat via son constructeur contrôlé
        aggregate = LabInstance(
            student_id=StudentId(model.student_id),
            lab_id=LabId(model.lab_id),
            objectives=objectives,
            status=model.status
        )

        # 3. Restauration de l'historique des tentatives (Attempts) avec normalisation UTC
        attempts_list = []
        for att_model in model.attempts:
            # SQLite omet le tzinfo : on garantit la conformité de l'invariant domaine
            ts = att_model.timestamp
            if ts and ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            attempt = Attempt(
                attempt_id=AttemptId(att_model.id),
                objective_id=ObjectiveId(att_model.objective_id),
                correlation_id=CorrelationId(att_model.correlation_id),
                timestamp=ts,
                is_correct=att_model.is_correct
            )
            attempts_list.append(attempt)

        # Injection contrôlée dans la collection privée de l'agrégat
        object.__setattr__(aggregate, '_attempts', attempts_list)

        return aggregate

    @staticmethod
    def to_persistence(aggregate: LabInstance, existing_model: LabInstanceModel | None = None) -> LabInstanceModel:
        """
        Transforme l'Aggregate Root LabInstance en modèle SQLAlchemy pour persistance.
        """
        pk = f"{aggregate.student_id.value}#-{aggregate.lab_id.value}"

        model = existing_model if existing_model else LabInstanceModel(id=pk)
        model.student_id = aggregate.student_id.value
        model.lab_id = aggregate.lab_id.value
        model.status = aggregate.status

        # Synchronisation de la collection d'objectifs
        model.objectives.clear()
        for obj in aggregate.objectives:
            obj_model = ObjectiveModel(
                objective_id=obj.objective_id.value,
                score_weight=obj.score_weight,
                is_completed=obj.is_completed
            )
            model.objectives.append(obj_model)

        # Synchronisation de l'historique des tentatives
        model.attempts.clear()
        for att in aggregate.attempts:
            att_model = AttemptModel(
                id=att.attempt_id.value,
                objective_id=att.objective_id.value,
                correlation_id=att.correlation_id.value,
                timestamp=att.timestamp,
                is_correct=att.is_correct
            )
            model.attempts.append(att_model)

        return model