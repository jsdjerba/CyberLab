from flask import Flask, jsonify, current_app
from werkzeug.exceptions import HTTPException

def register_error_handlers(app: Flask) -> None:
    """
    Register centralized, application-wide error handlers.
    Ensures that APIs always return JSON format, not HTML.
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        current_app.logger.warning(f"404 Error: {error}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        current_app.logger.error(f"500 Server Error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        """Catch-all for unhandled exceptions, returning standard JSON."""
        current_app.logger.error(f"Unhandled Exception: {error}")
        status_code = 500
        if isinstance(error, HTTPException):
            status_code = error.code
            
        return jsonify({"error": "Request failed"}), status_code