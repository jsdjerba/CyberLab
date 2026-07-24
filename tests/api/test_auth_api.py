import pytest
from unittest.mock import MagicMock
from flask import Flask
from api.v1.auth_api import create_auth_api
from api.error_handlers import register_error_handlers
from api.middleware.token_manager import TokenManager
from domain.dto.user_dto import UserDTO, AuthTokenDTO
from domain.exceptions import UserAlreadyExists, InvalidCredentials

@pytest.fixture
def auth_service_mock():
    return MagicMock()

@pytest.fixture
def app(auth_service_mock):
    flask_app = Flask(__name__)
    flask_app.testing = True
    
    # Enregistrement des handlers pour éviter les erreurs 500
    register_error_handlers(flask_app)
    
    flask_app.config['TOKEN_MANAGER'] = TokenManager("test-secret-key")
    
    # Injection du service dans le blueprint
    bp = create_auth_api(auth_service_mock)
    flask_app.register_blueprint(bp, url_prefix="/api/v1/auth")
    
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_success(client, auth_service_mock):
    auth_service_mock.register.return_value = UserDTO(1, "student01", "student@test.local")
    
    res = client.post("/api/v1/auth/register", json={
        "username": "student01",
        "email": "student@test.local",
        "password": "password123"
    })
    
    assert res.status_code == 201

def test_register_duplicate_user(client, auth_service_mock):
    auth_service_mock.register.side_effect = UserAlreadyExists("User already exists")
    
    res = client.post("/api/v1/auth/register", json={
        "username": "student01",
        "email": "student@test.local",
        "password": "password123"
    })
    
    assert res.status_code == 409
    assert "error" in res.get_json()

def test_login_success(client, auth_service_mock):
    auth_service_mock.authenticate.return_value = "mock_jwt_token"
    
    res = client.post("/api/v1/auth/login", json={
        "username": "student01",
        "password": "password123"
    })
    
    assert res.status_code == 200
    assert res.get_json()["token"] == "mock_jwt_token"

def test_login_invalid_password(client, auth_service_mock):
    auth_service_mock.authenticate.side_effect = InvalidCredentials("Wrong password")
    
    res = client.post("/api/v1/auth/login", json={
        "username": "student01",
        "password": "wrong"
    })
    
    assert res.status_code == 401

def test_me_valid_token(app, client):
    tm = app.config['TOKEN_MANAGER']
    token = tm.generate_token({"student_id": 1, "role": "student"})
    
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 200

def test_me_missing_token(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401