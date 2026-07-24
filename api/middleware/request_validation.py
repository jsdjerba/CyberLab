from functools import wraps
from flask import request
from domain.exceptions import ValidationError, InvalidCredentials, BaseDomainException

def validate_schema(payload: dict, schema: dict, strict: bool = True) -> dict:
    """
    Valide et nettoie un payload entrant selon un schéma défini.
    Rejette les champs non déclarés en mode strict.
    """
    if not isinstance(payload, dict):
        raise ValidationError("Payload must be a JSON object (dictionary).")

    cleaned_data = {}

    # 1. Vérification des champs requis et des types
    for key, expected_type in schema.items():
        if key not in payload:
            raise ValidationError(f"Missing required field: '{key}'.")
        
        if not isinstance(payload[key], expected_type):
            raise ValidationError(f"Invalid type for field '{key}'. Expected {expected_type.__name__}.")
        
        cleaned_data[key] = payload[key]

    # 2. Vérification des champs supplémentaires (Mode Strict)
    if strict:
        for key in payload.keys():
            if key not in schema:
                raise ValidationError(f"Unexpected field: '{key}'.")

    # 3. Retourne uniquement les données propres et déclarées
    return cleaned_data


def require_schema(schema: dict, strict: bool = True):
    """
    Décorateur Flask interceptant la requête pour valider son JSON.
    Injecte les données nettoyées dans `request.validated_data`.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Request payload must be JSON.")
            
            data = request.get_json()
            if data is None:
                data = {}
                
            # Validation stricte et assainissement
            cleaned_data = validate_schema(data, schema, strict)
            
            # Injection sécurisée pour le contrôleur
            request.validated_data = cleaned_data
            
            return f(*args, **kwargs)
        return decorated
    return decorator