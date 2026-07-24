import os
import shutil
import logging
from flask import Blueprint, jsonify

# Initialisation du blueprint
health_bp = Blueprint('health', __name__)

# Variable globale interne, injectée au démarrage de l'application
_health_service = None

def init_health_service(health_service_instance):
    """
    Injecte l'instance du service de santé au démarrage.
    Permet d'isoler complètement ce blueprint des détails de l'infrastructure.
    """
    global _health_service
    _health_service = health_service_instance

@health_bp.route('/health', methods=['GET'])
def system_health():
    return jsonify({"status": "healthy", "version": "1.0.0"})

@health_bp.route('/health/database', methods=['GET'])
def database_health():
    try:
        if _health_service is None:
            raise RuntimeError("Le service de santé de l'application n'est pas initialisé.")
            
        result = _health_service.check_database()
        return jsonify(result)
    except Exception as e:
        # Journalisation interne de l'erreur sans exposition des détails au client
        logging.getLogger("application").error(f"Échec de la vérification de l'infrastructure : {e}")
        return jsonify({"status": "unhealthy", "error": "Database service unavailable"}), 503

@health_bp.route('/health/storage', methods=['GET'])
def storage_health():
    try:
        from config.settings import UPLOAD_FOLDER
        
        _, _, free = shutil.disk_usage(UPLOAD_FOLDER)
        return jsonify({
            "status": "healthy",
            "disk_free_mb": free // (2**20),
            "writable": os.access(UPLOAD_FOLDER, os.W_OK)
        })
    except Exception as e:
        logging.getLogger("application").error(f"Échec de la vérification du stockage : {e}")
        return jsonify({"status": "unhealthy", "error": "Storage service unavailable"}), 503