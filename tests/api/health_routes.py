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
    app = Flask("test_creation")
    register_request_id_middleware(app)
    register_error_handlers(app)
    app.register_blueprint(labs_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_create_lab_instance_success(client):
    response = client.post("/api/v1/labs/lab-net-101/instances", json={"student_id": "student-alpha"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["student_id"] == "student-alpha"
    assert data["lab_id"] == "lab-net-101"
    assert data["status"] == "IN_PROGRESS"