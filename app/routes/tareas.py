from flask import Blueprint, jsonify, request
from app.services.tareas_service import get_tareas_service, insert_tareas_service
from flask_jwt_extended import jwt_required, get_jwt_identity


tareas_bp = Blueprint("tareas", __name__, url_prefix="/surco")


@tareas_bp.route("/tareas", methods=["GET"])
@jwt_required()
def get_tareas():
    result = get_tareas_service()
    return jsonify(result)

@tareas_bp.route("/tareas", methods=["POST"])
@jwt_required()
def insert_tareas():
    cod_cliente = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    result = insert_tareas_service(data, cod_cliente)
    return jsonify(result)
