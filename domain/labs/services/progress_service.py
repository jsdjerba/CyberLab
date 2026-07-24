from domain.labs.entities.lab import Lab
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.step_id import StepId
from domain.labs.value_objects.progress_report import ProgressReport

class ProgressService:
    """
    Domain Service pur. Calcule la progression via l'API publique des agrégats.
    Sans état (stateless) et sans mutation (side-effect free).
    """

    def evaluate_progress(self, instance: LabInstance, lab: Lab) -> ProgressReport:
        # 1. Nettoyage et déduplication via Set (protège contre les étapes obsolètes/dupliquées)
        instance_completed = instance.get_completed_steps()
        valid_completed_set = {
            step_id for step_id in instance_completed if lab.contains_step(step_id)
        }
        
        # 2. Conservation de l'ordre canonique défini par le Lab
        lab_steps = lab.get_steps()
        valid_completed = tuple(
            step.id for step in lab_steps if step.id in valid_completed_set
        )
        remaining = tuple(
            step.id for step in lab_steps if step.id not in valid_completed_set
        )
        
        # 3. Calculs des métriques
        total_steps = lab.step_count()
        valid_completed_count = len(valid_completed)
        remaining_count = len(remaining)
        
        if total_steps == 0:
            percentage = 100.0
            is_finished = True
        else:
            raw_percentage = (valid_completed_count / total_steps) * 100.0
            percentage = round(max(0.0, min(100.0, raw_percentage)), 2)
            is_finished = valid_completed_count >= total_steps
            
        # 4. Délégation du routage au Lab (prêt pour graphes/prérequis)
        next_steps = self.get_next_available_steps(instance, lab)
        
        return ProgressReport(
            completion_percentage=percentage,
            completed_steps=valid_completed,
            remaining_steps=remaining,
            next_available_steps=next_steps,
            is_finished=is_finished,
            completed_count=valid_completed_count,
            remaining_count=remaining_count
        )

    def get_next_available_steps(self, instance: LabInstance, lab: Lab) -> tuple[StepId, ...]:
        if self.is_lab_finished(instance, lab):
            return ()
        return lab.get_available_steps(instance.get_completed_steps())

    def is_lab_finished(self, instance: LabInstance, lab: Lab) -> bool:
        if lab.step_count() == 0:
            return True
            
        instance_completed = instance.get_completed_steps()
        valid_completed_count = sum(
            1 for step_id in set(instance_completed) if lab.contains_step(step_id)
        )
        
        return valid_completed_count >= lab.step_count()