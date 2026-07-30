"""
Middleware Flask pour l'attribution d'un Correlation/Request ID unique à chaque requête entrante.
Essentiel pour le traçage des logs en environnement scolaire offline.
"""

import uuid
from flask import request, g, jsonify


def register_request_id_middleware(app):
    """Enregistre les hooks avant/après requête pour le Request ID."""

    @app.before_request
    def inject_request_id():
        req_id = request.headers.get("X-Request-ID")
        if not req_id:
            req_id = f"req-{uuid.uuid4().hex[:12]}"
        g.request_id = req_id

    @app.after_request
    def append_request_id_header(response):
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id
        # Application des headers de sécurité de base
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response