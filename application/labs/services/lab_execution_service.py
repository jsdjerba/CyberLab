import uuid
from application.common.interfaces.unit_of_work import UnitOfWork
from application.common.interfaces.event_publisher import EventPublisher
from application.labs.exceptions import LabNotFoundError
from domain.labs.value_objects.lab_id import LabId
from domain.labs.value_objects.student_id import StudentId
from domain.labs.entities.lab_instance import LabInstance

class LabExecutionService:
    def __init__(
        self,
        uow: UnitOfWork,
        publisher: EventPublisher
    ):
        self.uow = uow
        self.publisher = publisher

    def start_lab(self, student_id_value: int, lab_id_value: str) -> str:
        # 1. Conversion primitives -> Value Objects
        student_id = StudentId(student_id_value)
        lab_id = LabId(lab_id_value)

        # 2. Ouverture de la transaction
        with self.uow:
            # 3. Charger le Lab
            lab = self.uow.labs.get_by_id(lab_id)
            if not lab:
                raise LabNotFoundError(f"Le laboratoire '{lab_id_value}' n'existe pas.")

            # 4. Chercher une instance existante
            instance = self.uow.lab_instances.get_by_student_and_lab(student_id, lab_id)

            # 5. Si aucune instance, on la crée
            if not instance:
                instance_id = f"inst_{uuid.uuid4().hex[:8]}"
                instance = LabInstance(instance_id, student_id, lab_id)

            # 6. Délégation au domaine (qui validera les règles et l'état)
            instance.start_lab(lab)

            # 7. Sauvegarde dans le repository
            self.uow.lab_instances.save(instance)

            # 8. Commit de la transaction
            self.uow.commit()

        # 9. Récupération et publication des événements après le context manager (après commit)
        events = instance.pull_events()
        for event in events:
            self.publisher.publish(event)

        # 10. Retour de l'ID
        return instance.id