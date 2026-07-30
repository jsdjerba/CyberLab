"""
Endpoints API REST Flask v1 pour les laboratoires.
"""

from flask import Blueprint, request, jsonify, g
from presentation.controllers.lab_controller import LabController
from infrastructure.container import ApplicationContainer

labs_bp = Blueprint("labs_api", __name__, url_prefix="/api/v1/labs")


def get_controller() -> LabController:
    container = ApplicationContainer()
    g.container = container
    return LabController(container)


@labs_bp.after_request
def cleanup_container(response):
    if hasattr(g, "container"):
        g.container.close()
    return response


@labs_bp.route("/<lab_id>/instances", methods=["POST"])
def create_instance(lab_id: str):
    controller = get_controller()
    data = request.get_json(silent=True) or {}
    result = controller.create_instance(lab_id, data)
    return jsonify(result), 201


@labs_bp.route("/<lab_id>/instances/<student_id>/start", methods=["POST"])
def start_instance(lab_id: str, student_id: str):
    controller = get_controller()
    data = request.get_json(silent=True) or {}
    result = controller.start_instance(lab_id, student_id, data, g.request_id)
    return jsonify(result), 200


@labs_bp.route("/<lab_id>/instances/<student_id>/flags", methods=["POST"])
def submit_flag(lab_id: str, student_id: str):
    controller = get_controller()
    data = request.get_json(silent=True) or {}
    result = controller.submit_flag(lab_id, student_id, data, g.request_id)
    return jsonify(result), 200


@labs_bp.route("/<lab_id>/instances/<student_id>", methods=["GET"])
def get_instance(lab_id: str, student_id: str):
    controller = get_controller()
    result = controller.get_instance_status(lab_id, student_id)
    return jsonify(result), 200