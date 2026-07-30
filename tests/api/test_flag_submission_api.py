"""
Tests d'API TDD pour la soumission de flags CTF (Phase 4).
"""

import pytest
from flask import Flask
from presentation.api.v1.labs_routes import labs_bp
from presentation.middleware.request_id import register_request_id_middleware
from presentation.middleware.error_handler import register_error_handlers
from infrastructure.database import Base, engine
from domain.value_objects.objective_id import ObjectiveId


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app = Flask("test_flag")
    register_request_id_middleware(app)
    register_error_handlers(app)
    app.register_blueprint(labs_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_submit_correct_flag_api(client):
    # 1. Création de l'instance de lab
    client.post("/api/v1/labs/lab-sec-303/instances", json={"student_id": "student-gamma"})
    
    # 2. Démarrage explicite de l'instance pour passer l'état à IN_PROGRESS
    client.post("/api/v1/labs/lab-sec-303/instances/student-gamma/start", json={"correlation_id": "corr-start-001"})

    # 3. Soumission du flag (avec un validateur par défaut qui reconnaît "secret" dans le flag)
    response = client.post(
        "/api/v1/labs/lab-sec-303/instances/student-gamma/flags",
        json={
            "objective_id": "obj-1",
            "flag": "CTF{secret_password_123}",
            "correlation_id": "corr-flag-001"
        }
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["validated"] is True