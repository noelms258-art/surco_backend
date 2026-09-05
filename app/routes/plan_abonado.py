from flask import Blueprint, jsonify, request
from app.services.plan_abonado_service import get_plan_abonado_service, insert_plan_abonado_service
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity


plan_abonado_bp = Blueprint("planAbonado", __name__, url_prefix="/surco")


@plan_abonado_bp.route("/planAbonado", methods=["GET"])
@jwt_required()
def get_plan_abonado():
    params = (request.args.get("codCampo"), datetime.now().year)
    result = get_plan_abonado_service(params)
    return jsonify(result)

@plan_abonado_bp.route("/planAbonado", methods=["POST"])
@jwt_required()
def insert_plan_abonado():
    data = request.get_json(silent=True) or {}
    result = insert_plan_abonado_service(data)
    return jsonify(result)