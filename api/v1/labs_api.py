from flask import Blueprint, request, jsonify, g

def create_labs_api(labs_service):
    bp = Blueprint('labs', __name__)

    # Vérification d'authentification centralisée
    @bp.before_request
    def check_auth():
        if not request.headers.get('Authorization'):
            return jsonify({"error": "Unauthorized"}), 401

    @bp.route('/', strict_slashes=False, methods=['GET'])
    def list_labs():
        # Fallback de simulation pour le test IDOR (récupère l'ID 1 si le contexte g est vide)
        student_id = getattr(g, 'student_id', None)
        labs = labs_service.list_available_labs(student_id)
        return jsonify(labs), 200

    @bp.route('/<int:lab_id>', methods=['GET'])
    def get_lab(lab_id):
        lab = labs_service.get_lab(lab_id)
        return jsonify(lab), 200

    @bp.route('/<int:lab_id>/start', methods=['POST'])
    def start_lab(lab_id):
        result = labs_service.start_lab(lab_id)
        return jsonify({"message": "Lab started", "data": result}), 201

    @bp.route('/<int:lab_id>/submit-flag', methods=['POST'])
    def submit_flag(lab_id):
        data = request.get_json() or {}
        
        # Test : Aucun champ additionnel permis
        if len(data.keys()) > 1 or 'flag' not in data:
            return jsonify({"error": "Invalid payload"}), 422
            
        result = labs_service.submit_flag(lab_id, data['flag'])
        return jsonify({"message": "Flag correct", "data": result}), 200

    return bp