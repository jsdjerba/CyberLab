from flask import Blueprint, jsonify

health_bp = Blueprint('health_api', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Public endpoint to verify system status and API availability.
    Does not require authentication.
    """
    return jsonify({
        "status": "ok",
        "application": "CyberLab",
        "version": "1.0"
    }), 200