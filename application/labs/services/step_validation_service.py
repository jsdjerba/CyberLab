from application.common.interfaces.unit_of_work import UnitOfWork
from application.common.interfaces.event_publisher import EventPublisher
from application.labs.interfaces.flag_validator import FlagValidator
from application.labs.exceptions import LabNotFoundError, LabInstanceNotFoundError
from application.labs.results.step_validation_result import StepValidationResult

from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.policies.submission_policy import SubmissionPolicy
from domain.labs.value_objects.lab_status import LabStatus

class StepValidationService:
    def __init__(
        self, 
        uow: UnitOfWork, 
        flag_validator: FlagValidator, 
        publisher: EventPublisher
    ):
        self.uow = uow
        self.flag_validator = flag_validator
        self.publisher = publisher
        # Injection de la politique de soumission par défaut avec cooldown_seconds.
        # Plus tard, cette donnée pourrait provenir des métadonnées du Lab.
        self.submission_policy = SubmissionPolicy(max_attempts=0, cooldown_seconds=0)

    def submit_flag(
        self, 
        student_id_value: int, 
        lab_id_value: str, 
        step_id_value: str, 
        submitted_flag: str
    ) -> StepValidationResult:
        # 1. Conversion des primitives en Value Objects
        student_id = StudentId(student_id_value)
        lab_id = LabId(lab_id_value)
        step_id = StepId(step_id_value)

        # 2. Ouverture de la transaction
        with self.uow:
            # 3. Chargement du Lab
            lab = self.uow.labs.get_by_id(lab_id)
            if not lab:
                raise LabNotFoundError(f"Le laboratoire '{lab_id_value}' n'existe pas.")

            # 4. Chargement de l'instance
            instance = self.uow.lab_instances.get_by_student_and_lab(student_id, lab_id)
            if not instance:
                raise LabInstanceNotFoundError(
                    f"Aucune session active pour l'étudiant {student_id_value} sur le lab '{lab_id_value}'."
                )

            # 5. Récupération de l'étape du domaine (lève StepNotFound si invalide)
            step = lab.get_step(step_id)

            # 6. Validation agnostique du flag
            is_valid = self.flag_validator.validate(step, submitted_flag)

            # CAS 1 : FLAG INCORRECT
            if not is_valid:
                instance.record_attempt(step_id, self.submission_policy)
                self.uow.lab_instances.save(instance)
                self.uow.commit()
                return StepValidationResult(
                    success=False,
                    message="Flag incorrect.",
                    score=instance.score,
                    current_step=instance.current_step.value if instance.current_step else None,
                    completed=instance.status == LabStatus.COMPLETED
                )

            # CAS 2 : FLAG CORRECT
            # Délégation complète des règles d'état (score, avancement) au domaine
            instance.complete_step(step_id, lab)
            self.uow.lab_instances.save(instance)
            self.uow.commit()

        # 7. Récupération et publication des événements UNIQUEMENT après commit
        events = instance.pull_events()
        for event in events:
            self.publisher.publish(event)

        # 8. Retour du DTO de succès
        return StepValidationResult(
            success=True,
            message="Étape validée avec succès.",
            score=instance.score,
            current_step=instance.current_step.value if instance.current_step else None,
            completed=instance.status == LabStatus.COMPLETED
        )