import pytest
from unittest.mock import MagicMock
from flask import Flask
from api.v1.gamification_api import create_gamification_api
from api.middleware.token_manager import TokenManager
from api.error_handlers import register_error_handlers
from domain.exceptions import LabNotFound, ValidationError
from core.events.exceptions import EventProcessingError

@pytest.fixture
def gamification_service_mock():
    return MagicMock()

@pytest.fixture
def app(gamification_service_mock):
    app = Flask(__name__)
    app.testing = True
    app.config['TOKEN_MANAGER'] = TokenManager("secret")
    register_error_handlers(app)
    
    # Injection de la fixture pour pouvoir la manipuler dans les tests
    app.register_blueprint(create_gamification_api(gamification_service_mock))
    return app

def test_profile_expired_token(app):
    tm = app.config['TOKEN_MANAGER']
    # Token expiré il y a 1 heure
    token = tm.generate_token({"student_id": 1}, expires_in=-3600)
    client = app.test_client()
    res = client.get("/api/v1/gamification/profile", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401

def test_leaderboard_limit_abuse(app, gamification_service_mock):
    # On simule le service de domaine qui rejette une limite aberrante
    gamification_service_mock.get_leaderboard.side_effect = ValidationError("Limit exceeded")
    
    tm = app.config['TOKEN_MANAGER']
    token = tm.generate_token({"student_id": 1})
    client = app.test_client()
    
    res = client.get("/api/v1/gamification/leaderboard?limit=999", headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 422
    assert res.get_json()["error"]["code"] == "VALIDATION_ERROR"