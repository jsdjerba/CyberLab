import pytest
from flask import Flask
from presentation.api.v1.health_routes import health_bp
from presentation.middleware.request_id import register_request_id_middleware


@pytest.fixture
def client():
    app = Flask("test_security")
    register_request_id_middleware(app)
    app.register_blueprint(health_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_security_headers_present(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "X-Request-ID" in response.headers