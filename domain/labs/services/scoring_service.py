from domain.labs.value_objects.scoring_context import ScoringContext
from domain.labs.policies.scoring_policy import ScoringPolicy
from domain.labs.exceptions import InvalidScoreContext

class ScoringService:
    """Domain Service responsable du calcul et de l'ajustement des scores selon les politiques."""

    def _validate_context(self, context: ScoringContext) -> None:
        """Valide l'intégrité du contexte de scoring (rejet des valeurs négatives)."""
        if (
            context.base_points < 0
            or context.attempts_count < 0
            or context.elapsed_time_seconds < 0
        ):
            raise InvalidScoreContext(
                f"Contexte invalide : base_points={context.base_points}, "
                f"attempts_count={context.attempts_count}, "
                f"elapsed_time={context.elapsed_time_seconds}"
            )

    def calculate_score(self, context: ScoringContext, policy: ScoringPolicy) -> int:
        """Calcule le score final en respectant l'ordre strict des règles métier."""
        # 1. Validation
        self._validate_context(context)

        # 2. Score initial
        score = context.base_points

        # 3. Pénalités d'essais multiples
        score = self.apply_penalties(score, context, policy)

        # 4. Bonus de rapidité
        score = self.apply_time_bonus(score, context, policy)

        # 5. Limitation par le score maximum possible défini par la politique
        if policy.max_score_possible > 0:
            score = min(score, policy.max_score_possible)

        # 6. Gestion du score plancher ou négatif
        if not policy.allow_negative_score:
            score = max(0, score)

        return score

    def apply_penalties(self, score: int, context: ScoringContext, policy: ScoringPolicy) -> int:
        """Applique les pénalités liées aux tentatives multiples."""
        penalty_total = context.attempts_count * policy.penalty_per_attempt
        return score - penalty_total

    def apply_time_bonus(self, score: int, context: ScoringContext, policy: ScoringPolicy) -> int:
        """Applique le bonus de temps si le seuil de rapidité est respecté."""
        if context.elapsed_time_seconds <= policy.time_bonus_threshold_seconds:
            return score + policy.time_bonus_value
        return score