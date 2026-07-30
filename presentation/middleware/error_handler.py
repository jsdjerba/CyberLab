"""
Gestionnaire d'erreurs global (Error Handler) pour l'API Flask.
Convertit les exceptions du Domaine et de l'Application en réponses HTTP JSON normalisées.
"""

from flask import jsonify, g
from domain.exceptions import (
    BaseDomainException,
    ValidationError,
    LabNotFound,
    LabInstanceNotFoundError,
    LabNotStartedException,
    LabAlreadyCompletedException,
    LabLockedOutException,
    CooldownException,
    InvalidLabStateException,
    UserAlreadyExists,
    InvalidCredentials,
    StudentNotFoundError
)


def register_error_handlers(app):
    """Enregistre les gestionnaires d'exceptions globaux sur l'application Flask."""

    def _error_payload(message: str, code: str) -> dict:
        req_id = getattr(g, "request_id", "req-unknown")
        return {
            "error": message,
            "code": code,
            "request_id": req_id
        }

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify(_error_payload(str(error), "VALIDATION_ERROR")), 422

    @app.errorhandler(UserAlreadyExists)
    def handle_user_exists(error):
        return jsonify(_error_payload(str(error), "USER_ALREADY_EXISTS")), 409

    @app.errorhandler(InvalidCredentials)
    def handle_invalid_creds(error):
        return jsonify(_error_payload("Invalid username or password.", "INVALID_CREDENTIALS")), 401

    @app.errorhandler(StudentNotFoundError)
    @app.errorhandler(LabNotFound)
    @app.errorhandler(LabInstanceNotFoundError)
    def handle_not_found(error):
        return jsonify(_error_payload(str(error), "NOT_FOUND")), 404

    @app.errorhandler(LabAlreadyCompletedException)
    def handle_lab_completed(error):
        return jsonify(_error_payload(str(error), "LAB_ALREADY_COMPLETED")), 409

    @app.errorhandler(LabNotStartedException)
    @app.errorhandler(LabLockedOutException)
    @app.errorhandler(CooldownException)
    @app.errorhandler(InvalidLabStateException)
    def handle_lab_state(error):
        return jsonify(_error_payload(str(error), "INVALID_LAB_STATE")), 400

    @app.errorhandler(BaseDomainException)
    def handle_domain_exception(error):
        return jsonify(_error_payload(str(error), "DOMAIN_ERROR")), 400

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        # Isolation stricte : aucun traceback brut exposé en production / environnement scolaire
        req_id = getattr(g, "request_id", "req-unknown")
        return jsonify({
            "error": "Internal server error.",
            "code": "INTERNAL_SERVER_ERROR",
            "request_id": req_id
        }), 500