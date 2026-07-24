import pytest
from flask import Flask
from api.middleware.error_handler import register_error_handlers
from api.exceptions.api_exception import NotFoundException, UnauthorizedException, ValidationException
from api.middleware.response_builder import ResponseBuilder

@pytest.fixture
def app():
    app = Flask(__name__)
    register_error_handlers(app)
    
    @app.route("/success")
    def success(): return ResponseBuilder.success(data={"id": 1})
    @app.route("/not-found")
    def not_found(): raise NotFoundException("Lab inconnu")
    @app.route("/unauthorized")
    def unauth(): raise UnauthorizedException("Token expiré")
    @app.route("/validation")
    def validation(): raise ValidationException("Format email erroné")
    @app.route("/error")
    def error(): raise Exception("Boom")
    return app

def test_success_response(app):
    res = app.test_client().get("/success")
    assert res.status_code == 200
    json = res.get_json()
    assert json == {"success": True, "code": "SUCCESS", "message": "Opération réussie", "data": {"id": 1}}

def test_not_found_exception(app):
    res = app.test_client().get("/not-found")
    assert res.status_code == 404
    assert res.get_json()["code"] == "NOT_FOUND"

def test_unauthorized_exception(app):
    res = app.test_client().get("/unauthorized")
    assert res.status_code == 401
    assert res.get_json()["code"] == "UNAUTHORIZED"

def test_validation_exception(app):
    res = app.test_client().get("/validation")
    assert res.status_code == 400
    assert res.get_json()["code"] == "VALIDATION_ERROR"