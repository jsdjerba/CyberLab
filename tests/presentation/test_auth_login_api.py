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

def test_login_success_returns_200_and_token(client):
    # Création via register
    client.post("/api/v1/auth/register", json={
        "email": "login_test@cyberlab.edu",
        "password": "ValidPassword123!",
        "role": "ADMIN"
    })
    
    # Tentative de login
    response = client.post("/api/v1/auth/login", json={
        "email": "login_test@cyberlab.edu",
        "password": "ValidPassword123!"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert data["role"] == "ADMIN"

def test_login_wrong_password_returns_401(client):
    client.post("/api/v1/auth/register", json={
        "email": "wrongpwd@cyberlab.edu",
        "password": "CorrectPassword123!",
        "role": "STUDENT"
    })
    
    response = client.post("/api/v1/auth/login", json={
        "email": "wrongpwd@cyberlab.edu",
        "password": "InvalidPassword!"
    })
    
    assert response.status_code == 401
    assert "Unauthorized" in response.get_json()["error"]