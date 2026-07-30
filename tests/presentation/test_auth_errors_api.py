import pytest
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database import Base
from infrastructure.container import ApplicationContainer
from presentation.api.v1.auth_routes import auth_bp
from presentation.error_handlers.api_exception_handler import register_api_error_handlers

@pytest.fixture
def client():
    app = Flask(__name__)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    app.container = ApplicationContainer(session=session)
    app.register_blueprint(auth_bp)
    register_api_error_handlers(app)
    
    with app.test_client() as client:
        yield client
    session.close()

def test_missing_fields_returns_400(client):
    response = client.post("/api/v1/auth/register", json={"email": "incomplete@test.com"})
    assert response.status_code == 400
    assert "Bad Request" in response.get_json()["error"]

def test_invalid_email_format_returns_400(client): # Déclenché par le Value Object Email
    response = client.post("/api/v1/auth/register", json={
        "email": "not_an_email",
        "password": "Password123!",
        "role": "STUDENT"
    })
    assert response.status_code == 400
    assert "invalide" in response.get_json()["message"].lower()

def test_login_unknown_user_returns_401(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "ghost@cyberlab.edu",
        "password": "Password123!"
    })
    assert response.status_code == 401
    assert "Unauthorized" in response.get_json()["error"]