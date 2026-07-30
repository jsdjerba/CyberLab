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

def test_register_success_returns_201(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "student@cyberlab.edu",
        "password": "SuperSecretPassword123!",
        "role": "STUDENT"
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == "student@cyberlab.edu"
    assert data["role"] == "STUDENT"
    assert "user_id" in data

def test_register_duplicate_email_returns_409(client):
    payload = {
        "email": "duplicate@cyberlab.edu",
        "password": "Password123!",
        "role": "TEACHER"
    }
    client.post("/api/v1/auth/register", json=payload) # 1er succès
    response = client.post("/api/v1/auth/register", json=payload) # 2ème échec
    
    assert response.status_code == 409
    assert "Conflict" in response.get_json()["error"]