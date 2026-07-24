from typing import Any
from flask import jsonify
from api.dto.base_dto import ApiResponseDTO

class ResponseBuilder:
    @staticmethod
    def success(data: Any = None, code: str = "SUCCESS", message: str = "Opération réussie"):
        dto = ApiResponseDTO(
            success=True, 
            code=code, 
            message=message, 
            data=data if data is not None else {}
        )
        return jsonify(dto.__dict__), 200

    @staticmethod
    def error(code: str, message: str, status_code: int = 400):
        # On ne passe pas de champ 'data' pour les erreurs
        dto = ApiResponseDTO(success=False, code=code, message=message)
        return jsonify(dto.__dict__), status_code