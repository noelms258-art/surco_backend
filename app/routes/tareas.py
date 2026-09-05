from flask import Blueprint, jsonify, request
from app.services.tareas_service import get_tareas_service


tareas_bp = Blueprint("tareas", __name__, url_prefix="/surco")


@tareas_bp.route("/tareas", methods=["GET"])
def get_tareas():
    result = get_tareas_service()
    return jsonify(result)

#@tareas_bp.route("/tareas", methods=["POST"])
#def insert_tareas():
#    result = get_tareas_service()
#    return jsonify(result)
