import hmac
from domain.labs.exceptions import InvalidFlagSubmission

class FlagValidationService:
    """
    Domain Service pur, stateless, responsable de la normalisation 
    et de la comparaison sécurisée des flags de cyber range.
    """

    def normalize_submission(self, raw_input: str) -> str:
        """
        Normalise une chaîne de soumission de manière déterministe :
        - Supprime les espaces superflus aux extrémités.
        - Supprime les retours chariot, tabulations et sauts de ligne.
        - Préserve intégralement les espaces internes.
        """
        if not isinstance(raw_input, str):
            raise InvalidFlagSubmission("Le flag soumis doit être une chaîne de caractères.")
        
        cleaned = raw_input.replace("\r", "")
        cleaned = cleaned.replace("\n", "")
        cleaned = cleaned.replace("\t", "")
        return cleaned.strip()

    def validate_flag(
        self,
        submitted_flag: str,
        expected_flag: str,
        *,
        case_sensitive: bool = False
    ) -> bool:
        """
        Valide un flag soumis par rapport à un flag attendu de manière sécurisée
        contre les attaques temporelles (timing attacks).
        """
        if submitted_flag is None or expected_flag is None:
            raise InvalidFlagSubmission("Les flags soumis et attendus ne peuvent pas être None.")
        
        if not isinstance(submitted_flag, str) or not isinstance(expected_flag, str):
            raise InvalidFlagSubmission("Les flags doivent être des chaînes de caractères.")

        norm_submitted = self.normalize_submission(submitted_flag)
        norm_expected = self.normalize_submission(expected_flag)

        if not case_sensitive:
            norm_submitted = norm_submitted.casefold()
            norm_expected = norm_expected.casefold()

        bytes_submitted = norm_submitted.encode('utf-8')
        bytes_expected = norm_expected.encode('utf-8')

        return hmac.compare_digest(bytes_submitted, bytes_expected)