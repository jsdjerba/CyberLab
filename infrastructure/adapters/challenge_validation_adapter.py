from typing import Any
from application.dtos.validation_result_dto import ValidationResult
from database.models.lab import Lab as LabModel
from database.models.flag import Flag as FlagModel

class ChallengeValidationAdapter:
    """
    Adaptateur d'infrastructure implémentant ChallengeValidationPort.
    Gère la persistance et délégue la validation métier au FlagValidationService du domaine.
    """

    def __init__(
        self,
        session: Any,
        flag_validation_service: Any
    ):
        self._session = session
        self._flag_validation_service = flag_validation_service

    def validate(
        self,
        lab_id: str,
        step_id: str,
        submitted_answer: str
    ) -> ValidationResult:
        # 1. Recherche du Lab ORM par son identifiant métier (lab_id)
        lab_model = self._session.query(LabModel).filter(LabModel.lab_id == lab_id).first()
        if not lab_model:
            return ValidationResult(success=False, reason="Lab not found")

        # 2. Recherche du Flag ORM associé par lab_id (clé primaire technique) et step_id
        flag_model = self._session.query(FlagModel).filter(
            FlagModel.lab_id == lab_model.id,
            FlagModel.step_id == step_id
        ).first()
        
        if not flag_model:
            return ValidationResult(success=False, reason="Flag not found")

        # 3. Délégation stricte de la validation au service domaine pur
        is_valid = self._flag_validation_service.validate_flag(
            submitted_flag=submitted_answer,
            expected_flag=flag_model.flag_hash
        )

        if not is_valid:
            return ValidationResult(success=False, reason="Invalid flag")

        # 4. Retour du DTO de succès
        return ValidationResult(success=True)