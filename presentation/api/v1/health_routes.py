"""
Endpoint de diagnostic (Health Check) pour les serveurs locaux et conteneurs Raspberry Pi.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health_api", __name__, url_prefix="/api/v1")


@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "platform": "CyberLab Education Platform",
        "mode": "Offline-First Enterprise"
    }), 200