import json
import pytest
from flask import Flask
from api.error_handlers import register_error_handlers
from domain.exceptions import InvalidCredentials, BaseDomainException
from core.events.exceptions import EventProcessingError

class FakeBusinessError(BaseDomainException):
    pass

@pytest.fixture
def client():
    app = Flask(__name__)
    register_error_handlers(app)
    
    @app.route("/leak-creds")
    def leak_creds():
        raise InvalidCredentials("password=123456")
        
    @app.route("/leak-db")
    def leak_db():
        raise EventProcessingError("MockEvent", "MockHandler", Exception("sqlite database locked"))
        
    @app.route("/fake-business")
    def fake_business():
        raise FakeBusinessError("Some unmapped domain rule failed")
        
    return app.test_client()

def test_credentials_do_not_leak(client):
    response = client.get("/leak-creds")
    data = json.loads(response.data)
    
    assert response.status_code == 401
    # Vérification que le message public est sain
    assert data["error"]["message"] == "Invalid username or password."
    # Vérification de l'absence de donnée sensible
    assert "123456" not in str(data)

def test_database_errors_do_not_leak(client):
    response = client.get("/leak-db")
    data = json.loads(response.data)
    
    assert response.status_code == 500
    assert data["error"]["message"] == "Internal server error."
    # Vérification de l'absence de fuite technique
    assert "sqlite" not in str(data).lower()
    assert "database" not in str(data).lower()

def test_unmapped_domain_exception(client):
    response = client.get("/fake-business")
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data["error"]["code"] == "DOMAIN_ERROR"
    assert data["error"]["message"] == "A business rule violation occurred."