from flask import jsonify
from domain.exceptions import (
    UserAlreadyExists, InvalidCredentials, ValidationError,
    LabNotFound, InvalidFlag, ProgressAlreadyCompleted, BaseDomainException
)

def register_error_handlers(app):
    @app.errorhandler(UserAlreadyExists)
    @app.errorhandler(ProgressAlreadyCompleted)
    def handle_conflict(e):
        return jsonify({"error": {"code": "CONFLICT", "message": str(e)}}), 409

    @app.errorhandler(InvalidCredentials)
    def handle_unauthorized(e):
        return jsonify({"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password."}}), 401
   
    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({"error": {"code": "VALIDATION_ERROR", "message": str(e)}}), 422

    @app.errorhandler(LabNotFound)
    def handle_not_found(e):
        return jsonify({"error": {"code": "NOT_FOUND", "message": str(e)}}), 404

    @app.errorhandler(InvalidFlag)
    def handle_bad_request(e):
        return jsonify({"error": {"code": "INVALID_FLAG", "message": str(e)}}), 400

    @app.errorhandler(BaseDomainException)
    def handle_base_domain(e):
        return jsonify({"error": {"code": "DOMAIN_ERROR", "message": "A business rule violation occurred."}}), 400
        
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        # Sécurité : aucune fuite technique
        return jsonify({"error": {"message": "Internal server error."}}), 500