"""
Validation structurelle HTTP légère via jsonschema.
Ne contient aucune règle métier (ex: format d'email), ces dernières restent dans le Domaine.
"""

REGISTER_SCHEMA = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "password": {"type": "string"},
        "role": {"type": "string"}
    },
    "required": ["email", "password", "role"],
    "additionalProperties": False
}

LOGIN_SCHEMA = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["email", "password"],
    "additionalProperties": False
}