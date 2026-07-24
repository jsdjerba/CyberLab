from domain.labs.entities.lab import Lab
from domain.labs.entities.lab_instance import LabInstance
from domain.labs.value_objects.student_history import StudentHistory
from domain.labs.value_objects.badge_id import BadgeId
from domain.labs.value_objects.achievement import Achievement

class AchievementService:
    """
    Domain Service pur, stateless, responsable de l'évaluation 
    des accomplissements (achievements) d'un étudiant.
    """

    def evaluate_achievements(
        self,
        instance: LabInstance,
        lab: Lab,
        history: StudentHistory
    ) -> tuple[Achievement, ...]:
        """
        Évalue l'instance de laboratoire terminée et l'historique 
        pour retourner les nouveaux accomplissements débloqués.
        """
        if not getattr(instance, "is_finished", False):
            return ()

        achievements = []
        lab_id_str = str(lab.id)
        successful_ids = {str(hid) for hid in history.successful_lab_ids}

        # 1. Première réussite (First Blood)
        if lab_id_str not in successful_ids:
            achievements.append(
                Achievement(
                    badge_id=BadgeId("FIRST_BLOOD"),
                    title="Première Réussite",
                    description=f"A réussi le laboratoire {lab.title} pour la première fois."
                )
            )

        # 2. Réussite parfaite (Perfect Score)
        instance_score = getattr(instance, "score", 0)
        max_score = lab.total_points
        if max_score > 0 and instance_score >= max_score:
            achievements.append(
                Achievement(
                    badge_id=BadgeId("PERFECT_SCORE"),
                    title="Score Parfait",
                    description="A complété le laboratoire avec un score maximal sans faute."
                )
            )

        # 3. Réussite rapide (Speed Run) - basé sur la durée estimée du lab si disponible
        estimated_duration = getattr(lab, "duration", 0)
        instance_duration = getattr(instance, "duration_seconds", 0)
        if estimated_duration > 0 and instance_duration > 0:
            # Si réalisé en moins de 80% du temps estimé
            if instance_duration <= (estimated_duration * 60 * 0.8):
                achievements.append(
                    Achievement(
                        badge_id=BadgeId("SPEED_RUN"),
                        title="Speed Run",
                        description="A terminé le laboratoire bien avant le temps estimé."
                    )
                )

        # 4. Jalons de volume (Milestone de labs terminés, ex: 5 labs)
        new_total_completed = history.completed_lab_count + 1
        if new_total_completed in {1, 5, 10, 25, 50}:
            achievements.append(
                Achievement(
                    badge_id=BadgeId(f"MILESTONE_{new_total_completed}_LABS"),
                    title=f"Cap des {new_total_completed} Labs",
                    description=f"A franchi le jalon de {new_total_completed} laboratoires complétés."
                )
            )

        # 5. Séries de réussites (Streak)
        current_streak = history.current_streak + 1
        if current_streak in {3, 5, 10}:
            achievements.append(
                Achievement(
                    badge_id=BadgeId(f"STREAK_{current_streak}"),
                    title=f"Série de {current_streak}",
                    description=f"A enchaîné {current_streak} réussites consécutives."
                )
            )

        return tuple(achievements)