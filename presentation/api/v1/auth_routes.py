"""
Endpoints d'authentification Flask.
Totalement agnostique de la BDD et de la cryptographie grâce à l'ApplicationContainer.
"""
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from jsonschema import validate

from presentation.schemas.auth_schema import REGISTER_SCHEMA, LOGIN_SCHEMA
from application.dto.auth_dto import RegisterUserCommand, LoginUserCommand

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

def _get_container():
    """Récupère l'orchestrateur de dépendances injecté au niveau de l'App Flask."""
    return current_app.container

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    validate(instance=data, schema=REGISTER_SCHEMA)

    command = RegisterUserCommand(
        email=data["email"],
        password=data["password"],
        role=data["role"],
        current_time=datetime.now(timezone.utc)
    )

    use_case = _get_container().register_user_use_case()
    result = use_case.execute(command)

    return jsonify({
        "user_id": result.user_id,
        "email": result.email,
        "role": result.role
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    validate(instance=data, schema=LOGIN_SCHEMA)

    command = LoginUserCommand(
        email=data["email"],
        password=data["password"],
        current_time=datetime.now(timezone.utc)
    )

    use_case = _get_container().login_user_use_case()
    result = use_case.execute(command)

    return jsonify({
        "user_id": result.user_id,
        "email": result.email,
        "role": result.role,
        "token": result.token
    }), 200