from domain.labs.entities.lab import Lab
from domain.labs.value_objects.student_id import StudentId
from domain.labs.value_objects.eligibility_context import EligibilityContext
from domain.labs.value_objects.level import Level
from domain.labs.exceptions import (
    LabNotPublished,
    PrerequisitesNotMet,
    AccessDenied
)

class LabEligibilityService:
    """
    Domain Service pur, stateless, responsable de l'évaluation 
    de l'éligibilité d'un étudiant à un laboratoire.
    """

    def check_eligibility(
        self,
        student_id: StudentId,
        lab: Lab,
        context: EligibilityContext
    ) -> bool:
        # 1. Vérification de la publication
        if not lab.is_published:
            raise LabNotPublished(str(lab.id))

        # 2. Vérification du niveau étudiant vs requis
        student_lvl = Level.from_str(context.student_level)
        required_lvl = Level.from_str(lab.required_level)

        if student_lvl < required_lvl:
            raise AccessDenied(f"Niveau insuffisant : requis {lab.required_level}, possédé {context.student_level}.")

        # 3. Vérification des prérequis
        completed_set = set(context.completed_lab_ids)
        for req_id in lab.required_lab_ids:
            if req_id not in completed_set:
                raise PrerequisitesNotMet(prerequisite_id=str(req_id))

        # 4. Vérification de la classe active (classroom)
        if lab.allowed_classrooms is not None:
            if context.active_classroom_id not in lab.allowed_classrooms:
                raise AccessDenied(f"Accès refusé pour la classe {context.active_classroom_id}.")

        return True