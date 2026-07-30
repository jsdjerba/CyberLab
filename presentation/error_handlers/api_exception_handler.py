"""
Mappage centralisé des exceptions du Domaine vers les codes HTTP RESTful.
Empêche les détails d'implémentation de fuiter vers le client.
"""
from flask import jsonify
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from domain.exceptions.auth_exceptions import (
    DuplicateUserException, UserNotFoundException,
    InvalidPasswordException, AuthenticationError
)

def register_api_error_handlers(app_or_blueprint):
    @app_or_blueprint.errorhandler(DuplicateUserException)
    def handle_duplicate_user(error):
        return jsonify({"error": "Conflict", "message": str(error)}), 409

    @app_or_blueprint.errorhandler(UserNotFoundException)
    def handle_user_not_found(error):
        return jsonify({"error": "Unauthorized", "message": str(error)}), 401

    @app_or_blueprint.errorhandler(InvalidPasswordException)
    def handle_invalid_password(error):
        return jsonify({"error": "Unauthorized", "message": str(error)}), 401

    @app_or_blueprint.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        return jsonify({"error": "Forbidden", "message": str(error)}), 403

    @app_or_blueprint.errorhandler(ValueError)
    def handle_value_error(error):
        # Intercepte les erreurs auto-validantes des Value Objects du Domaine
        return jsonify({"error": "Bad Request", "message": str(error)}), 400
        
    @app_or_blueprint.errorhandler(JsonSchemaValidationError)
    def handle_json_schema_error(error):
        return jsonify({"error": "Bad Request", "message": f"Format JSON invalide : {error.message}"}), 400