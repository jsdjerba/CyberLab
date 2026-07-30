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
    app = Flask("test_error")
    register_request_id_middleware(app)
    register_error_handlers(app)
    app.register_blueprint(labs_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_non_existent_instance_returns_404(client):
    response = client.get("/api/v1/labs/lab-none/instances/unknown-student")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert data["code"] == "NOT_FOUND"
    assert "request_id" in data