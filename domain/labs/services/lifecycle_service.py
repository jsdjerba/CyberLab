from domain.labs.entities.lab_instance import LabInstance
from domain.labs.entities.lab import Lab
from domain.labs.value_objects.lifecycle_context import LifecycleContext
from domain.labs.value_objects.lab_status import LabStatus
from domain.labs.exceptions import LabNotPublished, InvalidLabTransition, InvalidLabState

class LabLifecycleService:
    """Domain Service responsable d'orchestrer le cycle de vie d'une instance de laboratoire."""

    def start_lab(self, instance: LabInstance, lab: Lab, context: LifecycleContext) -> None:
        is_published = getattr(lab, "is_published", True)
        if not is_published:
            raise LabNotPublished(lab_id=lab.id)

        try:
            instance.start_lab(lab)
        except InvalidLabState as e:
            raise InvalidLabTransition(current_state=instance.status, requested_state="IN_PROGRESS", message=str(e))

    def pause_lab(self, instance: LabInstance, context: LifecycleContext) -> None:
        try:
            instance.pause()
        except InvalidLabState as e:
            raise InvalidLabTransition(current_state=instance.status, requested_state="PAUSED", message=str(e))

    def abandon_lab(self, instance: LabInstance, context: LifecycleContext) -> None:
        try:
            instance.abandon()
        except InvalidLabState as e:
            raise InvalidLabTransition(current_state=instance.status, requested_state="ABANDONED", message=str(e))

    def complete_lab(self, instance: LabInstance, lab: Lab, context: LifecycleContext) -> None:
        # Si l'instance est déjà marquée comme complétée par l'agrégat, l'orchestration réussit.
        if instance.status == LabStatus.COMPLETED:
            return

        if lab.steps and len(instance.completed_steps) < len(lab.steps):
            raise InvalidLabTransition(
                current_state=instance.status,
                requested_state="COMPLETED",
                message="Toutes les étapes obligatoires ne sont pas terminées."
            )
        try:
            instance.complete()
        except InvalidLabState as e:
            raise InvalidLabTransition(current_state=instance.status, requested_state="COMPLETED", message=str(e))