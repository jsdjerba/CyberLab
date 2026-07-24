import pytest
from unittest.mock import MagicMock
from flask import Flask
from api.v1.labs_api import create_labs_api
from api.error_handlers import register_error_handlers
from domain.exceptions import LabNotFound, InvalidFlag, ProgressAlreadyCompleted

@pytest.fixture
def labs_service_mock():
    return MagicMock()

@pytest.fixture
def app(labs_service_mock):
    flask_app = Flask(__name__)
    flask_app.testing = True
    
    # Enregistrement des handlers pour que les exceptions métier retournent les bons codes HTTP
    register_error_handlers(flask_app)
    
    bp = create_labs_api(labs_service_mock)
    flask_app.register_blueprint(bp, url_prefix="/api/v1/labs")
    
    return flask_app

def get_auth_headers(app):
    return {"Authorization": "Bearer fake_token"}

def test_list_labs_without_token(app):
    res = app.test_client().get("/api/v1/labs/")
    assert res.status_code == 401

def test_list_labs_success(app, labs_service_mock):
    labs_service_mock.list_available_labs.return_value = []
    res = app.test_client().get("/api/v1/labs/", headers=get_auth_headers(app))
    assert res.status_code == 200

def test_get_lab_success(app, labs_service_mock):
    labs_service_mock.get_lab.return_value = {"id": 1, "name": "Intro"}
    res = app.test_client().get("/api/v1/labs/1", headers=get_auth_headers(app))
    assert res.status_code == 200

def test_get_lab_not_found(app, labs_service_mock):
    labs_service_mock.get_lab.side_effect = LabNotFound("Not found")
    res = app.test_client().get("/api/v1/labs/999", headers=get_auth_headers(app))
    assert res.status_code == 404

def test_start_lab_success(app, labs_service_mock):
    labs_service_mock.start_lab.return_value = {"status": "STARTED"}
    res = app.test_client().post("/api/v1/labs/1/start", headers=get_auth_headers(app))
    assert res.status_code == 201

def test_submit_flag_success(app, labs_service_mock):
    labs_service_mock.submit_flag.return_value = {"success": True}
    res = app.test_client().post("/api/v1/labs/1/submit-flag", json={"flag": "CYBERLAB{win}"}, headers=get_auth_headers(app))
    assert res.status_code == 200

def test_submit_invalid_flag(app, labs_service_mock):
    labs_service_mock.submit_flag.side_effect = InvalidFlag("Wrong")
    res = app.test_client().post("/api/v1/labs/1/submit-flag", json={"flag": "BAD"}, headers=get_auth_headers(app))
    assert res.status_code == 400

def test_submit_completed_lab(app, labs_service_mock):
    labs_service_mock.submit_flag.side_effect = ProgressAlreadyCompleted("Done")
    res = app.test_client().post("/api/v1/labs/1/submit-flag", json={"flag": "DONE"}, headers=get_auth_headers(app))
    assert res.status_code == 409

def test_submit_flag_extra_field(app, labs_service_mock):
    res = app.test_client().post("/api/v1/labs/1/submit-flag", json={"flag": "ok", "extra": "evil"}, headers=get_auth_headers(app))
    assert res.status_code == 422

def test_xss_flag_payload(app, labs_service_mock):
    labs_service_mock.submit_flag.return_value = {"success": True}
    res = app.test_client().post("/api/v1/labs/1/submit-flag", json={"flag": "<script>"}, headers=get_auth_headers(app))
    assert res.status_code == 200