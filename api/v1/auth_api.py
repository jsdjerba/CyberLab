from flask import Blueprint, request, jsonify

def create_auth_api(auth_service):
    bp = Blueprint('auth', __name__)

    @bp.route('/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        # Lève UserAlreadyExists en interne
        user = auth_service.register(data.get('username'), data.get('password'))
        return jsonify({"username": user.username}), 201

    @bp.route('/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        # Lève InvalidCredentials en interne
        token = auth_service.authenticate(data.get('username'), data.get('password'))
        return jsonify({"token": token}), 200

    @bp.route('/me', methods=['GET'])
    def me():
        if not request.headers.get('Authorization'):
            return jsonify({"error": "Unauthorized"}), 401
        
        # Le TokenManager ou middleware valide le token
        return jsonify({"message": "Valid token"}), 200

    return bp