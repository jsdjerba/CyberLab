import pytest
from flask import Flask
from presentation.api.v1.labs_routes import labs_bp
from presentation.middleware.request_id import register_request_id_middleware
from presentation.middleware.error_handler import register_error_handlers
from infrastructure.database import Base, engine


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app = Flask("test_start")
    register_request_id_middleware(app)
    register_error_handlers(app)
    app.register_blueprint(labs_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_start_lab_instance_success(client):
    # Création préalable
    client.post("/api/v1/labs/lab-crypto-202/instances", json={"student_id": "student-beta"})
    
    # Démarrage explicite
    response = client.post("/api/v1/labs/lab-crypto-202/instances/student-beta/start", json={"correlation_id": "req-start-test"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "IN_PROGRESS"
    assert data["correlation_id"] == "req-start-test"