from flask import Flask
from api.v1.health_api import health_bp

def register_blueprints(app: Flask) -> None:
    """
    Central registry for all Flask Blueprints.
    This prevents circular imports and keeps the Application Factory clean.
    """
    # Register Core API v1 Blueprints
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    
    # Future registrations will happen here (e.g., auth_bp, student_bp)